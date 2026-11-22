import re, sys, html, pathlib, markdown
md = pathlib.Path(sys.argv[1]).read_text()
diagramas = []
def guarda(m):
    diagramas.append(m.group(1)); return f"\n\nDIAGRAMA{len(diagramas)-1}\n\n"
md = re.sub(r"```mermaid\n(.*?)```", guarda, md, flags=re.S)
corpo = markdown.markdown(md, extensions=["tables", "fenced_code"])
for i, d in enumerate(diagramas):
    corpo = corpo.replace(f"<p>DIAGRAMA{i}</p>", f'<div class="diagrama"><pre class="mermaid">{html.escape(d)}</pre></div>')
corpo = corpo.replace('<pre><code class="language-text">', '<pre class="saida">').replace("</code></pre>", "</pre>")
corpo = corpo.replace("<p>Natan Gaspar de Souza</p>", '<p class="sub">Natan Gaspar de Souza</p>', 1)
css = pathlib.Path("gs/docs/_estilo/documento.css").read_text()
extra = """
.diagrama pre.mermaid { background: none; border: 0; }
.diagrama svg { max-height: 150mm; }
.diagrama svg[aria-roledescription="flowchart-v2"] { min-width: 55%; max-height: 95mm; }
td code, li code, p code { background: #f0f3f7; padding: 0 2px; }
"""
out = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<title>{sys.argv[3]}</title>
<link rel="stylesheet" href="../_estilo/documento.css">
<style>{extra}</style>
</head><body>
{corpo}
<script src="MERMAID"></script>
<script>mermaid.initialize({{startOnLoad:false, theme:'neutral', themeVariables:{{fontSize:'15px'}}, fontFamily:'DejaVu Sans, Arial', flowchart:{{htmlLabels:false}}, sequence:{{useMaxWidth:true, actorFontSize:15, messageFontSize:15, noteFontSize:14, width:120}}, class:{{useMaxWidth:true}}}});
mermaid.run().then(()=>{{document.body.dataset.pronto='1'}}).catch(e=>{{console.error(String(e));document.body.dataset.pronto='1'}});</script>
</body></html>"""
pathlib.Path(sys.argv[2]).write_text(out)
