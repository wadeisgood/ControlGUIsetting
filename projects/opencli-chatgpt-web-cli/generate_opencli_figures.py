import os
from cli_anything.drawio.core.session import Session
from cli_anything.drawio.core import project as proj_mod, shapes as shapes_mod, connectors as conn_mod, export as export_mod

BASE = '/home/wade/.openclaw/workspace/opencli-chatgpt-web-cli/figures'
os.makedirs(BASE, exist_ok=True)

EDGE = [('strokeColor', '#6c8ebf'), ('strokeWidth', '1'), ('rounded', '1')]


def style_node(s, item, fill, font='14'):
    shapes_mod.set_style(s, item['id'], 'fillColor', fill, 0)
    shapes_mod.set_style(s, item['id'], 'strokeColor', '#333333', 0)
    shapes_mod.set_style(s, item['id'], 'fontSize', font, 0)


def style_edge(s, item, color='#6c8ebf', dashed=False):
    for k, v in EDGE:
        conn_mod.set_connector_style(s, item['id'], k, v, 0)
    conn_mod.set_connector_style(s, item['id'], 'strokeColor', color, 0)
    if dashed:
        conn_mod.set_connector_style(s, item['id'], 'dashed', '1', 0)


def fig1():
    s = Session(); proj_mod.new_project(s, preset='16:9')
    user = shapes_mod.add_shape(s, 'rounded', 70, 250, 170, 70, 'User / AI Agent', 0)
    cli = shapes_mod.add_shape(s, 'rounded', 290, 250, 190, 70, 'opencli Command Layer', 0)
    registry = shapes_mod.add_shape(s, 'rounded', 550, 120, 220, 80, 'Registry / Adapters\n(chatgpt-web, web, etc.)', 0)
    page = shapes_mod.add_shape(s, 'rounded', 550, 290, 220, 80, 'Browser / Page Abstraction\n(goto, evaluate, tabs, CDP)', 0)
    daemon = shapes_mod.add_shape(s, 'rectangle', 860, 120, 180, 80, 'OpenCLI Daemon', 0)
    ext = shapes_mod.add_shape(s, 'rectangle', 860, 290, 180, 80, 'Browser Extension\nBridge', 0)
    chrome = shapes_mod.add_shape(s, 'rounded', 1110, 120, 190, 80, 'Google Chrome\nLogged-in Session', 0)
    target = shapes_mod.add_shape(s, 'rounded', 1110, 290, 190, 80, 'Target Website\n(ChatGPT Web)', 0)

    for node, fill in [(user,'#dae8fc'),(cli,'#dae8fc'),(registry,'#fff2cc'),(page,'#fff2cc'),(daemon,'#d5e8d4'),(ext,'#d5e8d4'),(chrome,'#e1d5e7'),(target,'#f8cecc')]:
        style_node(s, node, fill)

    for a,b in [(user,cli),(cli,registry),(cli,page),(registry,daemon),(page,daemon),(daemon,ext),(ext,chrome),(chrome,target)]:
        e = conn_mod.add_connector(s, a['id'], b['id'], 'orthogonal', '', 0)
        style_edge(s, e)

    note = shapes_mod.add_shape(s, 'note', 510, 430, 420, 110, 'Execution path:\nCLI command → registry/adapter → browser/page abstraction → daemon → extension → Chrome session → target website', 0)
    style_node(s, note, '#f5f5f5', '13')

    drawio = os.path.join(BASE, 'figure-1-opencli-architecture.drawio')
    png = os.path.join(BASE, 'figure-1-opencli-architecture.png')
    proj_mod.save_project(s, drawio)
    export_mod.render(s, png, fmt='png', overwrite=True)


def fig2():
    s = Session(); proj_mod.new_project(s, preset='16:9')
    left_title = shapes_mod.add_shape(s, 'rounded', 120, 40, 360, 70, 'Built-in chatgpt adapter', 0)
    right_title = shapes_mod.add_shape(s, 'rounded', 760, 40, 360, 70, 'New chatgpt-web adapter', 0)
    left1 = shapes_mod.add_shape(s, 'rectangle', 150, 160, 300, 70, 'Platform: macOS', 0)
    left2 = shapes_mod.add_shape(s, 'rectangle', 150, 260, 300, 70, 'Mechanism: osascript / pbcopy / pbpaste', 0)
    left3 = shapes_mod.add_shape(s, 'rectangle', 150, 360, 300, 70, 'Target: ChatGPT Desktop App', 0)
    left4 = shapes_mod.add_shape(s, 'diamond', 210, 480, 180, 90, 'Fails on Ubuntu', 0)

    right1 = shapes_mod.add_shape(s, 'rectangle', 790, 160, 300, 70, 'Platform: Ubuntu / Linux', 0)
    right2 = shapes_mod.add_shape(s, 'rectangle', 790, 260, 300, 70, 'Mechanism: OpenCLI browser/page abstraction', 0)
    right3 = shapes_mod.add_shape(s, 'rectangle', 790, 360, 300, 70, 'Target: Chrome + ChatGPT Web', 0)
    right4 = shapes_mod.add_shape(s, 'diamond', 850, 480, 180, 90, 'Works via Web Adapter', 0)

    for node, fill in [(left_title,'#f8cecc'),(right_title,'#d5e8d4'),(left1,'#fff2cc'),(left2,'#fff2cc'),(left3,'#fff2cc'),(left4,'#f8cecc'),(right1,'#dae8fc'),(right2,'#dae8fc'),(right3,'#dae8fc'),(right4,'#d5e8d4')]:
        style_node(s, node, fill)
    for chain in [(left_title,left1,left2,left3,left4),(right_title,right1,right2,right3,right4)]:
        for a,b in zip(chain, chain[1:]):
            e = conn_mod.add_connector(s, a['id'], b['id'], 'orthogonal', '', 0)
            style_edge(s, e)

    drawio = os.path.join(BASE, 'figure-2-adapter-comparison.drawio')
    png = os.path.join(BASE, 'figure-2-adapter-comparison.png')
    proj_mod.save_project(s, drawio)
    export_mod.render(s, png, fmt='png', overwrite=True)


def fig3():
    s = Session(); proj_mod.new_project(s, preset='16:9')
    nodes = []
    labels = [
        'status\ncheck page state',
        'open\nopen ChatGPT Web',
        'new\nstart new conversation',
        'locate composer',
        'type prompt',
        'submit prompt',
        'wait assistant response',
        'extract assistant text'
    ]
    x = 80
    for i, label in enumerate(labels):
        n = shapes_mod.add_shape(s, 'rounded', x + i*150, 230 if i % 2 == 0 else 340, 130, 70, label, 0)
        style_node(s, n, '#dae8fc' if i < 3 else '#d5e8d4')
        nodes.append(n)
    for a,b in zip(nodes, nodes[1:]):
        e = conn_mod.add_connector(s, a['id'], b['id'], 'orthogonal', '', 0)
        style_edge(s, e)
    title = shapes_mod.add_shape(s, 'rounded', 420, 60, 420, 80, 'chatgpt-web ask flow', 0)
    style_node(s, title, '#fff2cc', '18')
    drawio = os.path.join(BASE, 'figure-3-ask-flow.drawio')
    png = os.path.join(BASE, 'figure-3-ask-flow.png')
    proj_mod.save_project(s, drawio)
    export_mod.render(s, png, fmt='png', overwrite=True)


def fig4():
    s = Session(); proj_mod.new_project(s, preset='16:9')
    start = shapes_mod.add_shape(s, 'rounded', 530, 40, 220, 70, 'ask debugging map', 0)
    a = shapes_mod.add_shape(s, 'rectangle', 110, 180, 230, 70, 'Selector found?', 0)
    b = shapes_mod.add_shape(s, 'rectangle', 410, 180, 260, 70, 'DOM updated but React state unsynced?', 0)
    c = shapes_mod.add_shape(s, 'rectangle', 760, 180, 220, 70, 'Send button disabled?', 0)
    d = shapes_mod.add_shape(s, 'rectangle', 250, 360, 260, 70, 'Submit fallback path\n(button / enter / enter+button)', 0)
    e = shapes_mod.add_shape(s, 'rectangle', 640, 360, 280, 70, 'Response detection\n(article text / assistant texts / stable count)', 0)
    fail1 = shapes_mod.add_shape(s, 'diamond', 50, 360, 140, 90, 'Fix selector', 0)
    fail2 = shapes_mod.add_shape(s, 'diamond', 1010, 360, 150, 90, 'Improve extraction', 0)
    for node, fill in [(start,'#fff2cc'),(a,'#dae8fc'),(b,'#dae8fc'),(c,'#dae8fc'),(d,'#d5e8d4'),(e,'#d5e8d4'),(fail1,'#f8cecc'),(fail2,'#f8cecc')]:
        style_node(s, node, fill)
    for a1,b1 in [(start,a),(a,b),(b,c),(b,d),(c,d),(d,e),(a,fail1),(e,fail2)]:
        edge = conn_mod.add_connector(s, a1['id'], b1['id'], 'orthogonal', '', 0)
        style_edge(s, edge)
    drawio = os.path.join(BASE, 'figure-4-debugging-map.drawio')
    png = os.path.join(BASE, 'figure-4-debugging-map.png')
    proj_mod.save_project(s, drawio)
    export_mod.render(s, png, fmt='png', overwrite=True)

def fig5():
    s = Session(); proj_mod.new_project(s, preset='16:9')
    cli = shapes_mod.add_shape(s, 'rounded', 110, 260, 190, 70, 'CLI / Adapter Layer\n(chatgpt-web ask)', 0)
    page = shapes_mod.add_shape(s, 'rounded', 430, 260, 230, 80, 'Page Abstraction Layer\n(goto / evaluate / insertText / screenshot)', 0)
    daemon = shapes_mod.add_shape(s, 'rectangle', 820, 140, 180, 70, 'OpenCLI Daemon', 0)
    bridge = shapes_mod.add_shape(s, 'rectangle', 820, 310, 180, 70, 'Extension / CDP Bridge', 0)
    chrome = shapes_mod.add_shape(s, 'rounded', 1110, 220, 210, 90, 'Google Chrome\nActive tab + session', 0)
    ret = shapes_mod.add_shape(s, 'note', 440, 420, 420, 110, 'Command forwarding loop:\nCLI → Page → sendCommand(...) → daemon → extension/CDP → Chrome → result back to Page', 0)
    for node, fill in [(cli,'#dae8fc'),(page,'#fff2cc'),(daemon,'#d5e8d4'),(bridge,'#d5e8d4'),(chrome,'#e1d5e7'),(ret,'#f5f5f5')]:
        style_node(s, node, fill)
    for a,b in [(cli,page),(page,daemon),(page,bridge),(daemon,chrome),(bridge,chrome)]:
        e = conn_mod.add_connector(s, a['id'], b['id'], 'orthogonal', '', 0)
        style_edge(s, e)
    back = conn_mod.add_connector(s, chrome['id'], page['id'], 'curved', 'result', 0)
    style_edge(s, back, '#b85450', dashed=True)
    drawio = os.path.join(BASE, 'figure-5-page-layering.drawio')
    png = os.path.join(BASE, 'figure-5-page-layering.png')
    proj_mod.save_project(s, drawio)
    export_mod.render(s, png, fmt='png', overwrite=True)


def fig6():
    s = Session(); proj_mod.new_project(s, preset='16:9')
    title = shapes_mod.add_shape(s, 'rounded', 420, 40, 430, 80, 'Figure B — chatgpt-web ask control loops', 0)
    style_node(s, title, '#fff2cc', '18')
    steps = [
        ('goto(ChatGPT)', 90, 220),
        ('waitForReady()', 280, 220),
        ('clickNewChat()', 470, 220),
        ('focusComposerAndType()', 660, 220),
        ('submitComposer()', 890, 220),
        ('waitForAssistantResponse()', 1090, 220),
        ('return assistant text', 1090, 400),
    ]
    nodes = []
    for label, x, y in steps:
        n = shapes_mod.add_shape(s, 'rounded', x, y, 170, 70, label, 0)
        style_node(s, n, '#dae8fc' if 'wait' not in label else '#d5e8d4')
        nodes.append(n)
    for a,b in zip(nodes, nodes[1:]):
        e = conn_mod.add_connector(s, a['id'], b['id'], 'orthogonal', '', 0)
        style_edge(s, e)
    loop_note = shapes_mod.add_shape(s, 'note', 240, 380, 340, 120, 'Polling loop A:\nwaitForReady() repeats pageSnapshot()\nuntil composer or login state is stable', 0)
    style_node(s, loop_note, '#f5f5f5', '13')
    loop_note2 = shapes_mod.add_shape(s, 'note', 730, 380, 320, 120, 'Polling loop B:\nwaitForAssistantResponse() repeats\npageSnapshot() until a new assistant text stabilizes', 0)
    style_node(s, loop_note2, '#f5f5f5', '13')
    loop1 = conn_mod.add_connector(s, nodes[1]['id'], nodes[1]['id'], 'curved', 'poll', 0)
    style_edge(s, loop1, '#b85450', dashed=True)
    loop2 = conn_mod.add_connector(s, nodes[5]['id'], nodes[5]['id'], 'curved', 'poll', 0)
    style_edge(s, loop2, '#b85450', dashed=True)
    drawio = os.path.join(BASE, 'figure-6-ask-control-loops.drawio')
    png = os.path.join(BASE, 'figure-6-ask-control-loops.png')
    proj_mod.save_project(s, drawio)
    export_mod.render(s, png, fmt='png', overwrite=True)

for fn in (fig1, fig2, fig3, fig4, fig5, fig6):
    fn()
print(BASE)
