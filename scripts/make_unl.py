#!/usr/bin/env python3
"""Génère le fichier .unl EVE-NG / PnetLab d'un lab à partir de son inventory.yml.

Usage (depuis la racine de network-labs) :
    python scripts/make_unl.py labs/incidents/INC-02-boucle-stp-bpdufilter

Lit :
  - <lab>/inventory.yml : section `eve` (nom du lab, nœuds avec template/icon/position, liens) ;
  - <lab>/configs/initial/<NOM>.txt (IOL) ou <NOM>.vpc (VPCS) : configurations de démarrage ;
  - eve-images.yml (racine du dépôt) : nom exact des images installées sur ton serveur.
Écrit <lab>/topology/<nom>.unl, à importer dans EVE-NG ou PnetLab.

Interfaces IOL : e<slot>/<port> → id = slot + 16 × port (convention EVE-NG).
Dépendance : PyYAML (pip install pyyaml).
"""
import base64, re, sys, uuid
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

import yaml


def iface_id(template_type, name, tpl=None):
    if tpl and tpl.get("ifaces"):
        if name not in tpl["ifaces"]:
            sys.exit(f"Interface {name} inconnue pour l'image {tpl.get('image')} (attendu : {', '.join(tpl['ifaces'])})")
        return tpl["ifaces"].index(name)
    if template_type == "vpcs":
        return 0
    if template_type == "qemu":  # vIOS / vIOS L2 : Gi<slot>/<port>, 4 ports par slot → id = 4 × slot + port
        m = re.fullmatch(r"(?:Gi|GigabitEthernet)(\d+)/(\d+)", name)
        if not m:
            sys.exit(f"Interface vIOS non reconnue : {name} (attendu Gi0/1)")
        return 4 * int(m.group(1)) + int(m.group(2))
    m = re.fullmatch(r"(?:e|Ethernet|eth)(\d+)/(\d+)", name)
    if not m:
        sys.exit(f"Interface IOL non reconnue : {name} (attendu e0/1 ou Ethernet0/1)")
    slot, port = int(m.group(1)), int(m.group(2))
    return slot + 16 * port


def short(name):
    m = re.fullmatch(r"(?:e|Ethernet)(\d+)/(\d+)", name)
    if m:
        return f"e{m.group(1)}/{m.group(2)}"
    m = re.fullmatch(r"(?:Gi|GigabitEthernet)(\d+)/(\d+)", name)
    return f"Gi{m.group(1)}/{m.group(2)}" if m else name


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    lab = Path(sys.argv[1])
    inv = yaml.safe_load((lab / "inventory.yml").read_text(encoding="utf-8"))
    images_file = Path("eve-images.yml")
    if not images_file.exists():
        sys.exit("eve-images.yml introuvable à la racine du dépôt.")
    images = yaml.safe_load(images_file.read_text(encoding="utf-8"))

    meta, eve = inv["lab"], inv["eve"]
    nodes = {name: {"name": name, "eve": spec} for name, spec in eve["nodes"].items()}
    ids = {name: i + 1 for i, name in enumerate(nodes)}
    ifaces = {name: [] for name in nodes}

    networks = []
    for k, (a, ai, b, bi) in enumerate(eve["links"], start=1):
        for n in (a, b):
            if n not in nodes:
                sys.exit(f"Lien vers un nœud inconnu : {n}")
        pa, pb = nodes[a]["eve"]["position"], nodes[b]["eve"]["position"]
        networks.append((k, f"Net-{a}-{b}", (pa[0] + pb[0]) // 2, (pa[1] + pb[1]) // 2))
        for n, i in ((a, ai), (b, bi)):
            tdef = images[nodes[n]["eve"]["template"]]
            ttype = tdef["type"]
            iname = i if tdef.get("ifaces") else (short(i) if ttype != "vpcs" else "eth0")
            ifaces[n].append((iface_id(ttype, i, tdef), iname, k))

    node_xml, cfg_xml = [], []
    for name, n in nodes.items():
        e = n["eve"]
        tpl = images[e["template"]]
        nid = ids[name]
        cfg_file = None
        for ext in (".txt", ".vpc"):
            p = lab / "configs" / "initial" / f"{name}{ext}"
            if p.exists():
                cfg_file = p
        has_cfg = 1 if cfg_file else 0
        if cfg_file:
            cfg_xml.append(f'      <config id="{nid}">{base64.b64encode(cfg_file.read_bytes()).decode()}</config>')
        x, y = e["position"]
        if tpl["type"] == "vpcs":
            attrs = f'type="vpcs" template="vpcs" image="" ethernet="1"'
        elif tpl["type"] == "qemu":
            attrs = (f'type="qemu" template={quoteattr(tpl["template"])} image={quoteattr(tpl["image"])} '
                     f'uuid="{uuid.uuid5(uuid.NAMESPACE_URL, "mtc/" + meta["id"] + "/" + name)}"')
            for key in ("cpu", "ram", "ethernet"):
                if key in tpl:
                    attrs += f' {key}="{tpl[key]}"'
            if tpl.get("qemu_options"):
                attrs += f' qemu_options={quoteattr(tpl["qemu_options"])} qemu_arch="x86_64"'
        else:
            attrs = (f'type="iol" template="iol" image={quoteattr(tpl["image"])} ethernet="{tpl.get("ethernet", 1)}" '
                     f'serial="0" nvram="{tpl.get("nvram", 1024)}" ram="{tpl.get("ram", 1024)}"')
        lines = [f'      <node id="{nid}" name={quoteattr(name)} {attrs} console="telnet" delay="0" '
                 f'icon={quoteattr(e["icon"])} config="{has_cfg}" left="{x}" top="{y}">']
        for iid, iname, net in sorted(ifaces[name]):
            lines.append(f'        <interface id="{iid}" name={quoteattr(iname)} type="ethernet" network_id="{net}"/>')
        lines.append("      </node>")
        node_xml.append("\n".join(lines))

    # Habillage façon topologie PnetLab : zones en pointillés, titres, fiches, légende
    txt_xml, preview = [], []
    tid = 0

    def add(kind, name, html):
        nonlocal tid
        tid += 1
        html = html.replace("{ID}", str(tid))
        txt_xml.append(f'      <textobject id="{tid}" name={quoteattr(name)} type="{kind}">\n'
                       f'        <data>{base64.b64encode(html.encode("utf-8")).decode()}</data>\n      </textobject>')
        preview.append(html)

    for z in eve.get("zones", []):
        x, y, w, h = z["x"], z["y"], z["w"], z["h"]
        col = z.get("color", "#0B37D4")
        dash = "10,6" if z.get("dash", True) else "0,0"
        add("square", z["label"],
            f'<div id="customShape{{ID}}" class="customShape customShape{{ID}} context-menu jtk-draggable" data-path="{{ID}}" '
            f'style="display: inline; position: absolute; left: {x}px; top: {y}px; cursor: move; z-index: 1;">'
            f'<svg width="{w}" height="{h}"><rect width="{w}" height="{h}" fill="{z.get("fill", col)}" fill-opacity="{z.get("opacity", 0.10)}" '
            f'stroke-width="3" stroke="{col}" stroke-dasharray="{dash}"></rect></svg></div>')
        add("text", z["label"] + " (titre)",
            f'<div id="customText{{ID}}" class="customShape customText context-menu jtk-draggable" data-path="{{ID}}" '
            f'style="display: inline; position: absolute; left: {x + 10}px; top: {y + 8}px; cursor: move; z-index: 1001; '
            f'color: {z.get("title_color", col)}; font-family: Arial, sans-serif; font-size: 15px; font-weight: bold; white-space: nowrap;">'
            f'<p style="margin: 0;">{escape(z["label"])}</p></div>')
    for t in eve.get("texts", []):
        mono = t.get("mono", True)
        font = "'DejaVu Sans Mono', Consolas, monospace" if mono else "Arial, sans-serif"
        box = (f'background-color: {t.get("bg", "#ffffff")}; border: 1px solid {t.get("border", "#8D99AB")}; '
               f'border-radius: 6px; padding: 4px 8px;') if t.get("box", True) else ""
        body = "<br>".join(escape(line) for line in str(t["text"]).split("\n"))
        add("text", t.get("name", t["text"].split("\n")[0][:30]),
            f'<div id="customText{{ID}}" class="customShape customText context-menu jtk-draggable" data-path="{{ID}}" '
            f'style="display: inline; position: absolute; left: {t["x"]}px; top: {t["y"]}px; cursor: move; z-index: 1002; '
            f'color: {t.get("color", "#1E2533")}; {box} font-family: {font}; font-size: {t.get("size", 12)}px; '
            f'font-weight: {"bold" if t.get("bold") else "normal"}; white-space: nowrap;">'
            f'<p style="margin: 0;">{body}</p></div>')

    net_xml = [f'      <network id="{k}" type="bridge" name={quoteattr(nm)} left="{x}" top="{y}" visibility="0"/>'
               for k, nm, x, y in networks]

    xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<lab name={quoteattr(eve["name"])} id="{uuid.uuid5(uuid.NAMESPACE_URL, 'masterytechcenter/' + meta['id'])}" version="1" scripttimeout="300" lock="0" author={quoteattr(meta.get("author", ""))}>
  <description>{escape(meta["id"] + " · " + meta["title"])}</description>
  <topology>
    <nodes>
{chr(10).join(node_xml)}
    </nodes>
    <networks>
{chr(10).join(net_xml)}
    </networks>
  </topology>
  <objects>
    <textobjects>
{chr(10).join(txt_xml)}
    </textobjects>
    <configs>
{chr(10).join(cfg_xml)}
    </configs>
  </objects>
</lab>
'''
    out = lab / "topology" / f'{eve["name"]}.unl'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(xml, encoding="utf-8")
    print(f"Écrit : {out} ({len(nodes)} nœuds, {len(networks)} liens, {tid} objets d'habillage)")
    if "--preview" in sys.argv[2:]:
        pos = {nm: n["eve"]["position"] for nm, n in nodes.items()}
        lines = "".join(
            f'<line x1="{pos[a][0]+30}" y1="{pos[a][1]+25}" x2="{pos[b][0]+30}" y2="{pos[b][1]+25}" stroke="#1F6FB2" stroke-width="2"/>'
            for a, _, b, _ in eve["links"])
        icons = "".join(
            f'<div style="position:absolute;left:{p[0]}px;top:{p[1]}px;width:60px;text-align:center;z-index:500;font:bold 12px Arial">'
            f'<img src="ICONS/{nodes[nm]["eve"]["icon"]}" style="width:60px;height:40px;object-fit:contain"><br>{nm}</div>'
            for nm, p in pos.items())
        (lab / "topology" / "preview.html").write_text(
            '<html><body style="margin:0;background:#fff;position:relative;width:1200px;height:900px">'
            f'<svg width="1200" height="900" style="position:absolute;z-index:100">{lines}</svg>{"".join(preview)}{icons}</body></html>',
            encoding="utf-8")


if __name__ == "__main__":
    main()
