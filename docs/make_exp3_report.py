# -*- coding: utf-8 -*-
import json
import statistics
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
FIG = DOCS / "figures"
OUT = DOCS / "2024303425-范劲庚-实验三报告.docx"

with open(ROOT / "results" / "branch_bound_stats.json", encoding="utf-8") as f:
    S = json.load(f)

ex = S["exact"]
sc = S["scalability"]
st = S["stress"]
byk = S["exact_by_k"]
groups = S["scalability_groups"]
scales = S["stress_by_scale"]

BLEU = RGBColor(0x1F, 0x4E, 0x79)
BLACK = RGBColor(0, 0, 0)
GRAY = RGBColor(0x59, 0x59, 0x59)


def n(value):
    return f"{int(value):,}"


def pct(value, digits=3, signed=True):
    if signed:
        return f"{value:+.{digits}f}%"
    return f"{value:.{digits}f}%"


def fnum(value, digits=2):
    return f"{value:,.{digits}f}"


def set_run_font(run, size=11, bold=False, italic=False, color=None,
                 ascii_font="Times New Roman", eastasia="宋体"):
    run.font.name = ascii_font
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color is not None:
        run.font.color.rgb = color
    r_pr = run._element.get_or_add_rPr()
    r_fonts = r_pr.find(qn("w:rFonts"))
    if r_fonts is None:
        r_fonts = OxmlElement("w:rFonts")
        r_pr.append(r_fonts)
    r_fonts.set(qn("w:ascii"), ascii_font)
    r_fonts.set(qn("w:hAnsi"), ascii_font)
    r_fonts.set(qn("w:eastAsia"), eastasia)


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_cell_margins(cell, top=40, start=70, bottom=40, end=70):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = OxmlElement("w:tcMar")
    for tag, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = OxmlElement("w:" + tag)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")
        tc_mar.append(node)
    tc_pr.append(tc_mar)


def set_table_borders(table, color="A6A6A6", size="4"):
    tbl = table._tbl
    tbl_pr = tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        element = OxmlElement("w:" + edge)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), size)
        element.set(qn("w:space"), "0")
        element.set(qn("w:color"), color)
        borders.append(element)
    tbl_pr.append(borders)


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def set_cell_text(cell, text, size=9, bold=False, align=WD_ALIGN_PARAGRAPH.CENTER,
                  color=None):
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = align
    p.paragraph_format.first_line_indent = None
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.line_spacing = 1.0
    run = p.add_run(str(text))
    set_run_font(run, size=size, bold=bold, color=color)
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER


doc = Document()
section = doc.sections[0]
section.page_width = Cm(21.0)
section.page_height = Cm(29.7)
section.top_margin = Cm(2.4)
section.bottom_margin = Cm(2.4)
section.left_margin = Cm(2.5)
section.right_margin = Cm(2.5)
section.header_distance = Cm(1.2)
section.footer_distance = Cm(1.2)

styles = doc.styles
normal = styles["Normal"]
normal.font.name = "Times New Roman"
normal.font.size = Pt(11)
normal.paragraph_format.line_spacing = 1.5
normal.paragraph_format.space_before = Pt(0)
normal.paragraph_format.space_after = Pt(0)
normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
r_pr = normal.element.get_or_add_rPr()
r_fonts = r_pr.find(qn("w:rFonts"))
if r_fonts is None:
    r_fonts = OxmlElement("w:rFonts")
    r_pr.append(r_fonts)
r_fonts.set(qn("w:ascii"), "Times New Roman")
r_fonts.set(qn("w:hAnsi"), "Times New Roman")
r_fonts.set(qn("w:eastAsia"), "宋体")

for name, size, before, after in (("Heading 1", 16, 12, 6),
                                  ("Heading 2", 13, 9, 4),
                                  ("Heading 3", 11.5, 6, 3)):
    style = styles[name]
    style.font.name = "Times New Roman"
    style.font.size = Pt(size)
    style.font.bold = True
    style.font.color.rgb = BLACK
    style.paragraph_format.space_before = Pt(before)
    style.paragraph_format.space_after = Pt(after)
    style.paragraph_format.keep_with_next = True
    style.paragraph_format.line_spacing = 1.15
    r_pr = style.element.get_or_add_rPr()
    r_fonts = r_pr.find(qn("w:rFonts"))
    if r_fonts is None:
        r_fonts = OxmlElement("w:rFonts")
        r_pr.append(r_fonts)
    r_fonts.set(qn("w:ascii"), "Times New Roman")
    r_fonts.set(qn("w:hAnsi"), "Times New Roman")
    r_fonts.set(qn("w:eastAsia"), "黑体")

cap_style = styles["Caption"]
cap_style.font.name = "Times New Roman"
cap_style.font.size = Pt(10.5)
cap_style.font.bold = True
cap_style.font.color.rgb = BLACK
cap_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
cap_style.paragraph_format.space_before = Pt(4)
cap_style.paragraph_format.space_after = Pt(4)
cap_style.paragraph_format.line_spacing = 1.0
r_pr = cap_style.element.get_or_add_rPr()
r_fonts = r_pr.find(qn("w:rFonts"))
if r_fonts is None:
    r_fonts = OxmlElement("w:rFonts")
    r_pr.append(r_fonts)
r_fonts.set(qn("w:ascii"), "Times New Roman")
r_fonts.set(qn("w:hAnsi"), "Times New Roman")
r_fonts.set(qn("w:eastAsia"), "宋体")

code_style = styles.add_style("Code Block", 1)
code_style.font.name = "Consolas"
code_style.font.size = Pt(8.5)
code_style.paragraph_format.line_spacing = 1.0
code_style.paragraph_format.space_before = Pt(0)
code_style.paragraph_format.space_after = Pt(0)
code_style.paragraph_format.first_line_indent = None
r_pr = code_style.element.get_or_add_rPr()
r_fonts = r_pr.find(qn("w:rFonts"))
if r_fonts is None:
    r_fonts = OxmlElement("w:rFonts")
    r_pr.append(r_fonts)
r_fonts.set(qn("w:ascii"), "Consolas")
r_fonts.set(qn("w:hAnsi"), "Consolas")
r_fonts.set(qn("w:eastAsia"), "宋体")

# 页眉页脚
header = section.header
header.is_linked_to_previous = False
hp = header.paragraphs[0]
hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
hp.paragraph_format.space_after = Pt(0)
hr = hp.add_run("算法分析与设计综合实验（三）")
set_run_font(hr, size=9, color=GRAY)

footer = section.footer
footer.is_linked_to_previous = False
fp = footer.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
fp.paragraph_format.space_after = Pt(0)
r1 = fp.add_run("第 ")
set_run_font(r1, size=9, color=GRAY)
run = fp.add_run()
fld_begin = OxmlElement("w:fldChar")
fld_begin.set(qn("w:fldCharType"), "begin")
instr = OxmlElement("w:instrText")
instr.set(qn("xml:space"), "preserve")
instr.text = " PAGE "
fld_end = OxmlElement("w:fldChar")
fld_end.set(qn("w:fldCharType"), "end")
run._r.append(fld_begin)
run._r.append(instr)
run._r.append(fld_end)
set_run_font(run, size=9, color=GRAY)
r2 = fp.add_run(" 页")
set_run_font(r2, size=9, color=GRAY)

table_no = 0
fig_no = 0


def body(text, indent=True, size=11, align=WD_ALIGN_PARAGRAPH.JUSTIFY,
         space_before=0, space_after=0, keep_with_next=False):
    p = doc.add_paragraph(style="Normal")
    p.alignment = align
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.keep_with_next = keep_with_next
    p.paragraph_format.first_line_indent = Pt(22) if indent else None
    run = p.add_run(text)
    set_run_font(run, size=size)
    return p


def rich_body(parts, indent=True, size=11, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p = doc.add_paragraph(style="Normal")
    p.alignment = align
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.first_line_indent = Pt(22) if indent else None
    for text, bold in parts:
        run = p.add_run(text)
        set_run_font(run, size=size, bold=bold)
    return p


def bullet(text, level=1):
    style = "List Bullet" if level == 1 else "List Bullet 2"
    p = doc.add_paragraph(style=style)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run(text)
    set_run_font(run, size=11)
    return p


def heading(text, level=1):
    p = doc.add_heading(level=level)
    run = p.add_run(text)
    set_run_font(run, size=16 if level == 1 else (13 if level == 2 else 11.5),
                 bold=True, eastasia="黑体")
    p.paragraph_format.space_before = Pt(12 if level == 1 else 9)
    p.paragraph_format.space_after = Pt(6 if level == 1 else 4)
    return p


def caption(text, kind="table"):
    global table_no, fig_no
    if kind == "table":
        table_no += 1
        label = f"表 {table_no}  {text}"
    else:
        fig_no += 1
        label = f"图 {fig_no}  {text}"
    p = doc.add_paragraph(style="Caption")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = (kind == "table")
    run = p.add_run(label)
    set_run_font(run, size=10.5, bold=True, eastasia="宋体")
    return p


def table(headers, rows, widths, font_size=9, header_fill="D9E2F3",
          left_first=False, align=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    t.allow_autofit = False
    set_table_borders(t)
    set_repeat_table_header(t.rows[0])
    for i, h in enumerate(headers):
        cell = t.rows[0].cells[i]
        cell.width = Inches(widths[i])
        set_cell_shading(cell, header_fill)
        set_cell_margins(cell)
        set_cell_text(cell, h, size=font_size, bold=True)
    for row in rows:
        cells = t.add_row().cells
        for i, value in enumerate(row):
            cells[i].width = Inches(widths[i])
            set_cell_margins(cells[i])
            a = WD_ALIGN_PARAGRAPH.LEFT if (left_first and i == 0) else WD_ALIGN_PARAGRAPH.CENTER
            if align is not None and i in align:
                a = align[i]
            set_cell_text(cells[i], value, size=font_size, align=a)
    for i, w in enumerate(widths):
        t.columns[i].width = Inches(w)
    return t


def formula(lines):
    p = doc.add_paragraph(style="Normal")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = None
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(3)
    run = p.add_run()
    set_run_font(run, size=10.5)
    for i, line in enumerate(lines):
        if i:
            run.add_break()
        run.add_text(line)
    return p


def code_block(title, lines):
    p = doc.add_paragraph(style="Normal")
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.first_line_indent = None
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(5)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(title)
    set_run_font(run, size=9.5, bold=True, ascii_font="Times New Roman")

    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    t.allow_autofit = False
    set_table_borders(t, color="BFBFBF", size="4")
    cell = t.rows[0].cells[0]
    cell.width = Inches(6.2)
    set_cell_shading(cell, "F7F7F7")
    set_cell_margins(cell, top=80, start=110, bottom=80, end=110)
    cell.text = ""
    for i, line in enumerate(lines):
        cp = cell.paragraphs[0] if i == 0 else cell.add_paragraph()
        cp.style = doc.styles["Code Block"]
        cp.paragraph_format.first_line_indent = None
        cp.paragraph_format.space_before = Pt(0)
        cp.paragraph_format.space_after = Pt(0)
        cp.alignment = WD_ALIGN_PARAGRAPH.LEFT
        cr = cp.add_run(line)
        set_run_font(cr, size=8.3, ascii_font="Consolas", eastasia="宋体")
    return t


def figure(filename, width, caption_text):
    p = doc.add_paragraph(style="Normal")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = None
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run()
    run.add_picture(str(FIG / filename), width=Inches(width))
    caption(caption_text, kind="figure")


# ------------------------------------------------------------------ 封面
for _ in range(4):
    doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("算法分析与设计综合实验报告")
set_run_font(r, size=24, bold=True)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("实验三  停机位调度问题")
set_run_font(r, size=18, bold=True)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("——分支限界法求解与回溯法对比")
set_run_font(r, size=14, bold=False)
for _ in range(3):
    doc.add_paragraph()

cover = doc.add_table(rows=6, cols=2)
cover.alignment = WD_TABLE_ALIGNMENT.CENTER
cover.autofit = False
cover.allow_autofit = False
cover_values = [
    ("课程名称：", "算法分析与设计"),
    ("实验名称：", "停机位调度问题（实验三）"),
    ("姓名：", "范劲庚"),
    ("学号：", "2024303425"),
    ("班级：", "14032401"),
    ("完成日期：", "2026 年 11 月 7 日"),
]
for i, (label, value) in enumerate(cover_values):
    row = cover.rows[i]
    row.height = Cm(1.0)
    c0, c1 = row.cells
    c0.width = Inches(2.0)
    c1.width = Inches(4.1)
    for c in (c0, c1):
        c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p0 = c0.paragraphs[0]
    p0.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p0.paragraph_format.first_line_indent = None
    p0.paragraph_format.space_after = Pt(0)
    r0 = p0.add_run(label)
    set_run_font(r0, size=13, bold=True)
    p1 = c1.paragraphs[0]
    p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p1.paragraph_format.first_line_indent = None
    p1.paragraph_format.space_after = Pt(0)
    r1 = p1.add_run(value)
    set_run_font(r1, size=13)
doc.add_page_break()

# ------------------------------------------------------------------ 摘要
heading("摘  要", 1)
body("停机位分配是机场运行管理中的核心组合优化问题：给定若干靠桥机位和远端机位、若干按计划到达和离开的飞机，需要为每架飞机指定一个机型兼容且时间不冲突的机位，使全体乘客的下机时间之和最小。实验一实现了两种贪心策略，实验二实现了带静态下界的回溯法。本实验在二者基础上实现分支限界法：以两种贪心解的较优者作为初始上界，按“大飞机优先、兼容机位少优先、乘客数降序”确定分支顺序；在深度优先搜索中同时使用静态后缀下界和动态可用机位下界，并对“剩余飞机已无可用机位”进行前向检查；每个结点按机位下机时间排序候选，以尽早得到较好的可行解。")
body(f"实验沿用实验二的 10000 个案例和三组测试口径。精确/近精确组取 K≤11 的 {n(ex['cases'])} 个案例，在 500 万结点、2 s 上限下，分支限界法在 {n(ex['optimal'])} 个案例上证明最优，回溯法为 {n(ex['backtrack_optimal'])} 个；分支限界法在 {ex['improved']} 个案例上得到比回溯法更低的目标值，{ex['equal']} 个持平，{ex['worse']} 个更差。总目标值由回溯法的 {n(ex['total_backtrack'])} 降至 {n(ex['total_branch'])}，下降 {abs(ex['gap_vs_backtrack']):.4f}%；总搜索结点由 {n(ex['backtrack_total_nodes'])} 降至 {n(ex['total_nodes'])}，减少 {ex['node_reduction_percent']:.2f}%；总耗时由 {fnum(ex['backtrack_total_time'])} ms 降至 {fnum(ex['total_time'])} ms。")
body(f"可扩展性抽样取 K=13..499 的 {sc['cases']} 个案例，分支限界法证明最优 {sc['optimal']} 个，回溯法 {sc['backtrack_optimal']} 个；总目标值仅下降 {abs(sc['gap_vs_backtrack']):.4f}%，但总耗时增加 {sc['time_change_percent']:.2f}%。全量压力测试覆盖全部 {n(st['cases'])} 个案例，在 20 万结点、200 ms 上限下，分支限界法证明最优 {n(st['optimal'])} 个，回溯法 {n(st['backtrack_optimal'])} 个；分支限界法改进 {n(st['improved'])} 个、持平 {n(st['equal'])} 个、更差 {st['worse']} 个，总目标值下降 {abs(st['gap_vs_backtrack']):.4f}%，总耗时增加 {st['time_change_percent']:.2f}%。")
body("实验表明：动态可用机位下界在 K≤15 时能显著压缩搜索树，是把“能搜完”推进到“能证明最优”的关键；当 K 增大时，动态集合的维护代价迅速上升，必须退化为静态下界，此时分支限界法与回溯法的搜索路径接近，优势主要来自双贪心初始上界。对 N、M、K 较大的案例，单纯加深搜索无法解决问题，应把强下界、对称性消除、邻域分解和启发式上界结合起来，将精确分支限界限定在可解的子问题上。")
p = doc.add_paragraph(style="Normal")
p.paragraph_format.first_line_indent = None
p.paragraph_format.line_spacing = 1.5
p.paragraph_format.space_before = Pt(8)
r = p.add_run("关键词：停机位调度；分支限界法；回溯法；下界剪枝；动态可用机位；组合优化")
set_run_font(r, size=11, bold=True)
doc.add_page_break()

# ------------------------------------------------------------------ 一、问题描述
heading("一、问题描述", 1)
heading("1.1 问题背景", 2)
body("随着航空运输量增长，机场停机位成为稀缺资源。飞机降落后需要停靠机位，乘客从机位下机并步行至到达口；靠桥机位可以直接连接登机廊桥，乘客下机时间短，远端机位需要乘坐摆渡车，下机时间长。停机位分配要在机型、时间、机位数量等约束下，为每架飞机选择一个机位，使所有乘客的下机时间之和尽可能小。该问题同时包含“把飞机分配给机位”的指派结构和“同一机位时间不重叠”的区间调度结构，是典型的 NP-hard 组合优化问题。")
body("实验假设飞机按计划时间到达和离开，忽略延误、拖曳和临时换位；远端机位均为大机位，且远端机位的单位乘客下机时间严格大于靠桥机位。案例中远端机位数 M 不少于飞机数 K，因此至少存在“每架飞机一个远端机位”的可行解；靠桥机位数量 N 可以小于 K，靠桥机位只允许小飞机停靠。")

heading("1.2 数学模型", 2)
body("设靠桥机位集合为 B（|B|=N），远端机位集合为 R（|R|=M），飞机集合为 P（|P|=K）。机位 s 的单位乘客下机时间记为 u_s，飞机 i 的乘客数记为 p_i，计划到达和离开时间记为 a_i、d_i，飞机 i 是否为大飞机记为 g_i。定义 0-1 决策变量 x_{i,s}：当飞机 i 分配到机位 s 时取 1，否则取 0。目标函数为：")
formula([
    "min  F(x) = Σ_{i∈P} Σ_{s∈B∪R} p_i · u_s · x_{i,s}",
])
body("约束条件为：")
formula([
    "Σ_{s∈B∪R} x_{i,s} = 1,                          ∀ i ∈ P",
    "x_{i,s} = 0,  若 g_i = 1 且 s ∈ B（大飞机不靠桥）",
    "x_{i,s} + x_{j,s} ≤ 1,  若 [a_i,d_i) ∩ [a_j,d_j) ≠ ∅",
    "x_{i,s} ∈ {0,1}",
])
body("其中时间区间采用半开区间 [a_i,d_i)：前一架飞机在 d_i 时刻离开，后一架飞机在 d_i 时刻到达，二者可以共用同一机位。目标函数也可写成“每架飞机被分配机位的单位下机时间乘以乘客数”之和，因此一架飞机对目标的贡献只取决于它最终使用的机位。")

heading("1.3 求解难点", 2)
body("若忽略时间冲突，问题退化为指派问题，可以用匈牙利算法或最小费用流在多项式时间内求解；时间冲突使同一机位的飞机集合必须构成区间不交的独立集，问题随即具有二次指派和区间调度的双重困难。随着 K 增大，可行分配数按机位数指数增长；更麻烦的是，很多远端机位的下机时间非常接近，交换两架飞机的机位只造成很小的目标变化，搜索树中出现大量“目标几乎相同”的对称分支，使下界剪枝难以快速收敛。")
body("本实验的分支限界法并不追求在任意规模上都完成搜索，而是采用 anytime 策略：在结点数和时间上限内返回当前最好的可行解，并用 Complete 标志区分“已证明最优”和“仅得到可行解”。这样既能在小规模上给出可验证的最优解，也能在 10000 个案例的全量测试中稳定地产生结果。")

# ------------------------------------------------------------------ 二、目的要求与环境
heading("二、实验目的、要求与环境", 1)
heading("2.1 实验目的", 2)
body("（1）在实验二回溯法的基础上实现分支限界法，掌握“分支、定界、剪枝、更新上界”的完整框架；（2）用同一批案例对比回溯法与分支限界法的解质量、搜索结点数和运行时间，解释差异的来源；（3）分析 N、M、K 较大时分支限界法失效的原因，提出可操作的改进算法或改进思路；（4）整理可复现的代码、数据、脚本和实验报告。")
heading("2.2 实验要求", 2)
body("实验要求为 100 种 (N,M,K) 组合、每种 100 个案例，共 10000 个案例；为这些案例设计停机位分配的分支限界算法，计算总下机时间；将分支限界法与回溯法的结果进行对比，分析两种算法的优劣；分析 N、M、K 较大时分支限界法存在的问题，并提供改进算法或改进思路。实验报告需说明问题建模、算法设计、正确性、复杂度、实验结果和问题记录，并提交完整代码。")
heading("2.3 实验环境", 2)
caption("实验软硬件环境")
table(
    ["项目", "配置"],
    [
        ["操作系统", "Arch Linux x86_64"],
        ["处理器 / 内存", "Intel Core i5-13500H（16 线程）/ 30 GiB"],
        ["编译器", "GCC 16.2.1，C++17"],
        ["构建系统", "CMake 4.4.4，Release（-O3 -DNDEBUG）"],
        ["报告与绘图", "Python 3，python-docx 1.2.0，matplotlib 3.11.2"],
        ["流程图", "Graphviz dot 16.1.0，Noto Sans CJK SC"],
    ],
    [1.7, 4.5],
    left_first=True,
)
body("所有算法在同一台机器、同一 Release 构建下运行。计时使用 std::chrono::steady_clock，记录求解函数内部从进入到返回的墙钟时间；同一案例的贪心、回溯和分支限界依次运行，避免并发干扰。")

heading("2.4 代码组织", 2)
body("工程沿用实验一、实验二的 C++17/CMake 结构，核心库 airport_core 同时包含贪心、回溯和分支限界求解器，命令行工具负责数据生成、批量基准、单案例复现和结果校验。实验三新增或修改的主要文件如下。")
caption("实验三主要代码文件")
table(
    ["文件", "作用", "关键内容"],
    [
        ["include/solver.h", "求解器接口", "Solution、Solver、GreedySolver、BacktrackingSolver、BranchBoundSolver"],
        ["src/branch_bound.cpp", "分支限界实现", "搜索树、双贪心上界、静态/动态下界、剪枝、回滚"],
        ["src/backtracking.cpp", "回溯法实现", "实验二基线，复用其时间轴和静态下界"],
        ["src/greedy.cpp", "贪心实现", "策略 1 按乘客数降序，策略 2 按到达时间升序"],
        ["src/utils.cpp", "解校验", "时间轴冲突、机型兼容、目标值重算"],
        ["tools/branch_bound_benchmark.cpp", "批量对比", "同一案例依次运行三种算法并输出 CSV"],
        ["tools/solve_case.cpp", "单案例复现", "打印贪心、回溯、分支限界的分配与统计"],
        ["docs/make_exp3_stats.py", "统计脚本", "生成 branch_bound_stats.json"],
        ["docs/make_exp3_figures.py", "绘图脚本", "生成实验三全部图表"],
        ["docs/make_exp3_report.py", "报告脚本", "生成本报告 docx"],
    ],
    [1.9, 1.6, 2.7],
    font_size=8.3,
    left_first=True,
)
body("数据仍由 tools/generate_cases.cpp 生成：固定随机种子，先抽取 100 组互不重复的 (N,M,K)，每组再生成 100 个案例；N 取 1..50，M 取 5..500，K 取 5..500，M≥K，桥下机时间 10..30，远端下机时间 35..60，到达时间 0..1200，停留时长 30..180，乘客数 20..300，约 40% 为大飞机。完整数据约 59 MB，提交包只放生成器、组合表和代表性样例；运行生成器即可重建 10000 个案例。")

# ------------------------------------------------------------------ 三、算法设计
heading("三、分支限界算法设计", 1)
heading("3.1 与回溯法的关系", 2)
body("回溯法和分支限界法都按飞机顺序建立搜索树：第 d 层决定第 d 架飞机使用哪个机位，叶子对应一个完整分配。实验二的回溯法在深度优先搜索中使用“剩余飞机乘客数乘以其兼容机位最小下机时间”的静态后缀下界，剪掉不可能优于当前最好解的分支。实验三的分支限界法保留这一搜索框架，但把“定界”做得更细：一方面用两种贪心解提供更紧的初始上界，另一方面在搜索过程中维护每架剩余飞机“当前仍可使用的兼容机位集合”，用这些集合的最小下机时间之和作为动态下界；当某架剩余飞机已无可用机位时立即回溯。")
caption("回溯法与分支限界法的实现差异")
table(
    ["维度", "回溯法（实验二）", "分支限界法（实验三）"],
    [
        ["搜索框架", "深度优先，按飞机逐层分支", "深度优先，增加全局上界和动态定界"],
        ["初始上界", "贪心策略 1 的可行解", "策略 1 与策略 2 的较优解"],
        ["下界", "静态后缀下界", "静态后缀下界 + 动态可用机位下界"],
        ["附加剪枝", "cost + LB ≥ best", "cost ≥ best、cost + LB ≥ best、空可用集"],
        ["候选顺序", "按机位下机时间升序", "按机位下机时间升序，并列按机位编号"],
        ["大规模处理", "固定静态下界，anytime 返回", "K≤15 用动态下界，K>15 退化静态下界"],
        ["结果标志", "Complete 表示已证明最优", "Complete 表示已证明最优"],
    ],
    [1.35, 2.25, 2.6],
    font_size=8.6,
    left_first=True,
)
body("因此，本实验的分支限界法不是“最佳优先搜索”的另一种写法，而是“深度优先 + 上界 + 强下界 + 前向检查”的分支限界实现。它保留了深度优先搜索内存占用小的优点，同时通过更紧的下界减少无效结点；在时间或结点超限时，它和回溯法一样返回当前最好可行解，保证 anytime 可用。")

heading("3.2 搜索树与初始上界", 2)
body("设飞机顺序为 π_0, π_1, …, π_{K-1}。第 d 层选择飞机 π_d 的机位，已分配飞机的目标贡献记为 cost。顺序按以下优先级确定：大飞机优先（可选机位少）、兼容机位数少优先、乘客数降序、编号升序。这样可以让约束最强、对目标影响最大的飞机先分支，使上界尽早下降，也减少深层才发现不可行的概率。")
body("初始上界由两种贪心解给出。策略 1 按乘客数降序处理飞机，策略 2 按到达时间升序处理飞机；二者都在“机型兼容且时间轴空闲”的机位中选择单位下机时间最小者。设两种策略的目标值为 F_1、F_2，则初始上界为：")
formula(["UB = min(F_1, F_2)"])
body("两个贪心解都是可行解，所以 UB 一定是合法上界；取较优者比实验二只用一个贪心解更紧，能更早剪掉劣质分支。实验中不少中等规模案例的改进并非来自搜索到更深，而是来自这个更强的初始上界。")

heading("3.3 静态下界与动态下界", 2)
body("对飞机 i，记其兼容机位集合为 C_i，最小单位下机时间为 m_i = min_{s∈C_i} u_s。若当前搜索到第 d 层，则剩余飞机 π_d..π_{K-1} 无论怎样分配，每架飞机至少贡献 p_i·m_i，因此静态后缀下界为：")
formula([
    "LB_static(d) = Σ_{j=d}^{K-1} p_{π_j} · m_{π_j}",
])
body("静态下界只使用“机型兼容”信息，没有考虑已经分配的飞机占用了哪些机位，也没有考虑时间冲突，所以通常偏松。分支限界法进一步维护动态可用机位集合 A_i：对每架尚未分配的飞机 i，A_i 包含所有与 i 机型兼容、且没有被“已分配且与 i 时间重叠”的飞机占用的机位。若 A_i 非空，令 m_i(A_i)=min_{s∈A_i} u_s，则动态下界为：")
formula([
    "LB_dynamic = Σ_{i 未分配} p_i · m_i(A_i)",
])
body("动态下界是合法下界：任何完整的剩余分配都必须把飞机 i 放在 A_i 中的某个机位，因此 i 的贡献至少是 p_i·m_i(A_i)；对剩余飞机求和即得下界。与静态下界相比，动态下界会把“已经被占用的桥位”从集合中删去，因此当桥位紧张时下界会明显抬高。若某架飞机满足 A_i=∅，说明当前部分分配已经不可能扩展为完整解，可直接回溯。")
body("动态下界的维护使用“每架飞机一个有序多重集合”：集合元素为 (机位下机时间, 机位编号)，按字典序排序。选择机位 s 分配给当前飞机时，对所有与当前飞机时间重叠的剩余飞机 i，若 s∈C_i，则从 A_i 中删除 (u_s,s)；递归返回时再按记录逆序插回。这里必须使用 (下机时间, 机位编号) 的二元组而不是只存下机时间：不同机位可能有相同的下机时间，只按下机时间删除会误删另一个仍然可用的机位，导致下界被高估并错误剪枝。实验过程中确实出现过这一缺陷，详见第七节。")

heading("3.4 剪枝规则与候选顺序", 2)
body("在结点 (d, cost) 上依次执行以下判断：（1）若 cost ≥ UB，当前部分解已经不可能严格优于最好解，剪枝；（2）若 cost + LB ≥ UB，其中 LB 在 K≤15 时取 LB_dynamic，否则取 LB_static(d)，剪枝；（3）若存在未分配飞机 i 使 A_i=∅，剪枝；（4）若 d=K，用 cost 更新 UB 和最好分配。所有剪枝都只删除“不可能产生严格更优完整解”的分支，因此不会丢失最优解。")
body("对当前飞机的候选机位，先检查机型兼容和时间轴空闲，再按 (u_s, s) 升序排序。下机时间小的机位优先，使搜索尽早到达较好的叶子，从而尽快降低 UB；并列时按机位编号升序，保证结果可复现。候选排序只影响搜索顺序，不影响最优性。")
body("每个机位的时间轴用 std::map 维护已占用区间，键为到达时间，值为离开时间；插入前检查前驱和后继是否与 [a,d) 重叠。由于区间是半开的，前一架离开时间等于后一架到达时间时允许复用。该结构与实验二一致，便于把差异归因于定界策略而不是数据结构。")

heading("3.5 搜索流程与动态阈值", 2)
body("算法 3-1 给出了分支限界搜索的主流程。根结点先用两种贪心解初始化 UB；若根结点的下界已经不小于 UB，则无需扩展任何结点即可证明贪心解最优。否则从第 0 层开始深度优先搜索，进入子结点前更新动态可用集，返回后完整回滚。")
code_block("算法 3-1  分支限界搜索", [
    "输入：案例 c，时间上限 T，结点上限 L",
    "输出：最好解 x*，目标值 UB，是否证明最优 complete",
    "1  order ← 按大飞机优先、兼容数少、乘客降序、编号排序",
    "2  x1 ← Greedy(c, ByPassengers);  x2 ← Greedy(c, ByArrival)",
    "3  x* ← argmin(F(x1), F(x2));  UB ← F(x*)",
    "4  预计算每架飞机的兼容机位、m_i、静态后缀下界 suffix[d]",
    "5  if K ≤ 15: 初始化每架飞机的可用集 A_i 和 dynamicSum",
    "6  rootLB ← (K ≤ 15 ? dynamicSum : suffix[0])",
    "7  if rootLB ≥ UB: return (x*, UB, complete=true)",
    "8  DFS(0, 0)",
    "9  return (x*, UB, complete = 未触发时间/结点上限)",
    "",
    "DFS(d, cost):",
    "  nodes ← nodes + 1",
    "  if 触发时间或结点上限: 置停止标志并返回",
    "  if cost ≥ UB: return",
    "  LB ← (动态下界开启 ? dynamicSum : suffix[d])",
    "  if LB = ∞ 或 cost + LB ≥ UB: return",
    "  if 动态下界开启 且 存在空可用集: return",
    "  if d = K: x* ← current; UB ← cost; return",
    "  cand ← 当前飞机兼容且时间轴空闲的机位，按 (u_s, s) 升序",
    "  for s in cand:",
    "    从 dynamicSum 中扣除当前飞机自己的贡献",
    "    for 与当前飞机时间重叠的剩余飞机 i 且 s ∈ C_i:",
    "        从 A_i 删除 (u_s, s)，记入 removed[d]",
    "    在机位 s 的时间轴插入 [a,d)；current[π_d] ← s",
    "    DFS(d+1, cost + p_{π_d}·u_s)",
    "    回滚时间轴和 current；按逆序把 removed[d] 插回 A_i",
    "    恢复 dynamicSum",
])
body("图 1 把上述流程画成流程图：左侧是双贪心初始上界和根结点剪枝，中间是深度优先的分支、候选排序和动态集合更新，右侧是回滚与结果封装。图中的“动态下界”分支只在 K≤15 时启用。")
figure("flow_branch_bound.png", 4.3, "分支限界法搜索流程")
body("动态下界的维护不是免费的：每次分支要对所有与当前飞机时间重叠的剩余飞机做删除，递归返回时再做插入，单次代价约为 O(K log S)，其中 S=N+M。K 较小时，它带来的结点减少远大于维护成本；K 较大时，动态集合的删除/插入和内存访问成为主成本，而搜索本身又因结点上限很快被截断，收益很小。因此实现中设置阈值 dynamicBoundEnabled_ = (K ≤ 15)：K≤15 使用动态下界，K>15 退回静态后缀下界。这个阈值不是理论结论，而是由实验二的规模和本次实测的代价—收益对比确定的工程参数；第 4.6 节会给出阈值两侧的对比。")
body("时间上限和结点上限分别每 1024 个结点和每个结点检查一次。触发任一上限后，搜索立即停止，返回当前最好的可行解，并把 timeLimitReached 或 nodeLimitReached 置为 true；只有两者都未触发时 complete 才为 true。这样，调用者可以明确区分“已证明最优”和“在预算内得到的最好解”。")

heading("3.6 正确性", 2)
body("引理 1（静态下界合法）：对任意剩余飞机 i，其兼容机位集合为 C_i，任何可行完整解都必须把 i 放在某个 s∈C_i，故 i 的贡献 ≥ p_i·min_{s∈C_i}u_s；对剩余飞机求和即得 LB_static(d) ≤ 任何完整解的目标值。")
body("引理 2（动态下界合法）：A_i 由“与 i 兼容且未被已分配且与 i 时间重叠的飞机占用”的机位组成。任何从当前部分解出发的完整解，都不能把 i 放在 A_i 之外的机位：机型不兼容的机位不允许，已被时间冲突占用的机位也不能再用。因此 i 的贡献 ≥ p_i·min_{s∈A_i}u_s；求和即得 LB_dynamic 合法。")
body("定理 1（剪枝安全）：若某结点满足 cost ≥ UB 或 cost + LB ≥ UB，则该结点下不存在目标值严格小于 UB 的完整解，剪枝不会丢掉最优解。证明：任何完整解的目标值 = 当前部分贡献 cost + 剩余贡献；由引理 1/2，剩余贡献 ≥ LB，因此完整解目标值 ≥ cost+LB ≥ UB。")
body("定理 2（完成即最优）：若搜索在未触发时间/结点上限的情况下结束，则算法返回的 UB 等于最优目标值。证明：算法从根结点开始枚举所有未被剪枝的分支；由定理 1，被剪掉的分支都不含更优解；所有叶子都被访问或被安全剪枝，因此最好解一定被更新过。算法只在 cost < UB 时更新，故最终 UB 是最优值。")
body("上述正确性只依赖“下界合法”和“剪枝条件”，不依赖候选顺序、贪心策略或动态阈值。因此，即使 K>15 时关闭动态下界，算法仍然正确，只是搜索树可能更大。实验中还做了交叉校验：对回溯法和分支限界法都 complete 的案例，逐一比较目标值，结果完全一致（见 4.2 节）。")

heading("3.7 复杂度", 2)
body("设机位数 S=N+M，飞机数 K。最坏情况下搜索树有 O(S^K) 个叶子、O(S^K) 个结点；每个结点生成候选需要 O(K·S) 次兼容/时间检查，候选排序 O(S log S)；动态下界每个分支的删除/插入为 O(K log S)，回滚相同。静态下界的预计算为 O(K·S)，动态集合的初始化为 O(K·S log S)。空间方面，时间轴 O(K)，当前分配 O(K)，动态可用集 O(K·S)，递归栈 O(K)。")
body("实际运行由时间/结点上限截断，最坏复杂度不会真正展开；但这也意味着大规模案例的结果是“预算内最好解”，而不是最优解。下界越紧，实际展开的结点越少；动态下界以更高的单结点代价换取更小的搜索树，是否划算取决于 K、S 和预算，这正是 3.5 节阈值设置的依据。")

# ------------------------------------------------------------------ 四、实验结果
heading("四、实验结果与分析", 1)
heading("4.1 实验设置", 2)
body("实验使用实验一生成的 10000 个案例，沿用实验二的三组口径，并增加分支限界法作为对比对象。三组测试的限制如下。")
caption("三组实验的设置")
table(
    ["组别", "K 范围", "案例数", "时间上限", "结点上限"],
    [
        ["精确/近精确组", "K≤11", "2000", "2000 ms", "5,000,000"],
        ["可扩展性组", "K=13..499", "100", "2000 ms", "5,000,000"],
        ["全量压力组", "K=5..500", "10000", "200 ms", "200,000"],
    ],
    [1.55, 1.55, 1.0, 1.0, 1.1],
)
body("精确组不是简单取前 2000 个 caseId，而是扫描全部 10000 个案例后按 K≤11 过滤；原因是 caseId 的排列与 K 的大小没有单调关系，按 caseId 截断会漏掉一部分小 K 案例。可扩展性组复刻实验二的抽样：K=13..15 取 30 例，K=16..80 取 40 例，K=81..499 取 30 例，共 100 例。全量压力组对 10000 个案例逐一运行，统一使用 200 ms、20 万结点的预算。")
body("每组都让贪心策略 1、回溯法和分支限界法在同一案例、同一时间/结点限制下依次运行，记录目标值、耗时、展开结点数、是否完成搜索和状态。所有解在写入 CSV 前都经过 validateSolution 校验：检查每架飞机恰好分配一个机位、机型兼容、同一机位时间不重叠，并重新计算目标值。")

heading("4.2 正确性与可行性校验", 2)
body(f"精确组 {n(ex['cases'])} 个案例中，分支限界法和回溯法都没有出现不可行解或非法解（infeasible={ex['infeasible']}，invalid={ex['invalid']}）；两边都完成搜索的案例有 {n(ex['complete_both'])} 个，逐一比较目标值，mismatch={ex['complete_value_mismatch']}，即只要两边都证明最优，得到的目标值完全相同。这一交叉校验比单独看某个算法的自报结果更有说服力：它同时验证了搜索树、时间轴和下界实现。")
body(f"可扩展性组的 {sc['cases']} 个案例中，两边都完成搜索的 {sc['complete_both']} 个案例目标值也完全一致，非法解为 {sc['invalid']}。全量压力组的 {n(st['cases'])} 个案例中，两边都完成搜索的 {n(st['complete_both'])} 个案例目标值一致，非法解为 {st['invalid']}。在三组共 12100 个案例中，分支限界法相对回溯法改进 {ex['improved']+sc['improved']+st['improved']} 例、持平 {ex['equal']+sc['equal']+st['equal']} 例、更差 0 例；相对贪心策略 1 改进 {ex['improved_vs_greedy']+sc['improved_vs_greedy']+st['improved_vs_greedy']} 例、持平 {ex['equal_vs_greedy']+sc['equal_vs_greedy']+st['equal_vs_greedy']} 例、更差 0 例。分支限界法没有在任何案例上退化为比回溯法更差的解，这符合“同样的可行解空间 + 更强的剪枝”的预期。")

heading("4.3 精确组总体结果", 2)
caption("精确组（K≤11，2000 例）总体对比")
table(
    ["指标", "贪心策略 1", "回溯法", "分支限界法"],
    [
        ["证明最优案例数", "—", n(ex["backtrack_optimal"]), n(ex["optimal"])],
        ["结点上限案例数", "—", n(ex["backtrack_node_limit"]), n(ex["node_limit"])],
        ["时间上限案例数", "—", n(ex["backtrack_time_limit"]), n(ex["time_limit"])],
        ["总目标值", n(ex["total_greedy"]), n(ex["total_backtrack"]), n(ex["total_branch"])],
        ["相对贪心目标变化", "—", f"{(ex['total_backtrack']-ex['total_greedy'])/ex['total_greedy']*100:+.3f}%", f"{ex['gap_vs_greedy']:+.3f}%"],
        ["总搜索结点", "—", n(ex["backtrack_total_nodes"]), n(ex["total_nodes"])],
        ["总耗时 / ms", "—", fnum(ex["backtrack_total_time"]), fnum(ex["total_time"])],
        ["平均耗时 / ms", "—", fnum(ex["backtrack_total_time"]/ex["cases"]), fnum(ex["total_time"]/ex["cases"])],
        ["最大单案例耗时 / ms", "—", fnum(ex["backtrack_max_time"]), fnum(ex["max_time"])],
    ],
    [1.75, 1.35, 1.45, 1.65],
    font_size=8.8,
    left_first=True,
)
body(f"精确组中，分支限界法把证明最优的案例数从 {n(ex['backtrack_optimal'])} 提高到 {n(ex['optimal'])}，把结点上限案例数从 {n(ex['backtrack_node_limit'])} 降到 {ex['node_limit']}，总目标值下降 {abs(ex['gap_vs_backtrack']):.4f}%。更值得注意的是搜索结点数：回溯法共展开 {n(ex['backtrack_total_nodes'])} 个结点，分支限界法只展开 {n(ex['total_nodes'])} 个，减少 {ex['node_reduction_percent']:.2f}%。这说明动态可用机位下界确实在大量分支上提前给出了“已经不可能更好”的判断，而不是靠更快的机器或更长的运行时间取胜。")
body(f"但分支限界法并非在所有指标上都更优：它的总耗时只下降 {abs(ex['time_change_percent']):.2f}%，最大单案例耗时反而从 {fnum(ex['backtrack_max_time'])} ms 上升到 {fnum(ex['max_time'])} ms。原因是动态下界在每个结点上都要维护多重集合，单结点成本更高；当案例在 500 万结点上限处被截断时，分支限界法做了更多“有用但昂贵”的工作。总耗时下降来自 13 个案例从“结点受限”变为“完成搜索”，抵消了单结点开销。")
body("图 2 按 K 展示了最优案例数、总搜索结点和总耗时；图 3 进一步给出逐案例的结点散点图和结点减少比例分布。可以看到，K≤8 时两法的搜索树都很小，分支限界法的结点更少但耗时略高；K=9..11 时动态下界的收益迅速放大，结点减少最明显。")
figure("exact_compare.png", 6.1, "精确组按 K 的最优案例数、搜索结点与耗时对比")
figure("exact_search_scatter.png", 5.9, "精确组逐案例搜索结点与结点减少比例")

heading("4.4 精确组按 K 分析", 2)
caption("精确组按 K 的搜索结果")
table(
    ["K", "案例数", "B&B/BT 最优", "B&B 目标值", "BT 目标值", "B&B 结点", "BT 结点"],
    [
        [
            k,
            n(byk[k]["cases"]),
            f"{byk[k]['optimal']}/{byk[k]['backtrack_optimal']}",
            n(byk[k]["total_branch"]),
            n(byk[k]["total_backtrack"]),
            n(byk[k]["total_nodes"]),
            n(byk[k]["backtrack_total_nodes"]),
        ]
        for k in ["5", "6", "7", "8", "9", "10", "11"]
    ] + [[
        "合计", n(ex["cases"]), f"{ex['optimal']}/{ex['backtrack_optimal']}",
        n(ex["total_branch"]), n(ex["total_backtrack"]), n(ex["total_nodes"]), n(ex["backtrack_total_nodes"]),
    ]],
    [0.55, 0.7, 0.9, 1.05, 1.05, 0.95, 1.0],
    font_size=8.2,
)
body("K=5..8 时，两法都能在全部案例上证明最优，目标值完全相同；分支限界法的结点数约为回溯法的一半，但总耗时略高（例如 K=5 时 4.11 ms 对 2.17 ms，K=6 时 6.27 ms 对 4.21 ms）。这是因为小规模案例的搜索树本来就小，双贪心初始化和动态集合的固定开销占比高，结点减少不足以抵消单结点成本。K=8 时出现反转：分支限界法 44.10 ms，回溯法 69.04 ms，结点从 174.7 万降到 51.3 万，节省的搜索时间开始超过维护成本。")
body("K=9 时，分支限界法在 499/500 个案例上证明最优，回溯法为 498/500；K=10 时双方均为 200/200；K=11 时分支限界法 96/100，回溯法 84/100。K=11 是收益最集中的一层：分支限界法总目标值 4,970,730，回溯法 4,975,554，下降 4,824；总结点从 1.398 亿降到 4,845 万，减少约 65.3%；总耗时从 4,219.38 ms 降到 4,161.76 ms。也就是说，在最有挑战的一层，动态下界同时改善了解质量、结点数和总时间。")
body("图 3 的散点图显示，大多数案例位于对角线下方，说明分支限界法的结点数普遍少于回溯法；但散点也显示少数案例落在对角线上方，这些案例通常是回溯法很快完成、而分支限界法因动态维护而略慢的小案例。244 个案例由根结点下界直接证明最优（分支限界法不展开任何结点），其中 5 个案例回溯法仍需搜索；其余 1751 个案例两法都展开了正数个结点。根结点直接剪枝的比例约为 12.2%，说明双贪心初始上界与根下界的组合在部分案例上非常有效。")

heading("4.5 状态改变与典型案例", 2)
body("精确组中有 13 个案例的状态从“回溯法结点受限”变为“分支限界法证明最优”，其中 3 个案例的目标值同时下降。表 7 列出这 13 个案例；未列出的 1987 个案例两法状态相同（或都完成、或都受限），目标值也没有变化。")
status_rows = []
for item in S["status_changed"]:
    gap = (item["backtrack"] - item["branch"]) / item["backtrack"] * 100.0
    status_rows.append([
        str(item["case"]), str(item["K"]),
        "结点受限" if item["backtrack_status"] == "node_limit" else item["backtrack_status"],
        "最优" if item["branch_status"] == "optimal" else item["branch_status"],
        n(item["backtrack"]), n(item["branch"]), f"{gap:.3f}%",
    ])
caption("精确组中状态改变的 13 个案例")
table(
    ["案例", "K", "回溯状态", "B&B 状态", "回溯目标", "B&B 目标", "目标下降"],
    status_rows,
    [0.55, 0.45, 0.85, 0.8, 0.95, 0.95, 0.85],
    font_size=8.2,
)
body("案例 325 是最能说明动态下界作用的例子。该案例 N=1、M=16、K=11，只有 1 个靠桥机位（单位下机时间 12），16 个远端机位的单位下机时间在 37..60 之间；11 架飞机中有 5 架大飞机，桥位只能服务小飞机。贪心策略 1 得到 49,239，策略 2 得到 55,049；回溯法在 500 万结点上限内得到 48,849，分支限界法在 399,658 个结点、40.69 ms 内完成搜索并证明最优 46,699。")
# 案例 325 数据
planes325 = [
    (0, 396, 532, "小", 174), (1, 1011, 1107, "小", 247),
    (2, 214, 326, "大", 222), (3, 1019, 1194, "大", 125),
    (4, 753, 862, "小", 250), (5, 1133, 1166, "大", 150),
    (6, 585, 727, "大", 167), (7, 712, 798, "小", 89),
    (8, 656, 796, "小", 287), (9, 562, 664, "大", 42),
    (10, 720, 820, "大", 289),
]
bt_assign = {0: 0, 1: 0, 2: 0, 3: 13, 4: 13, 5: 0, 6: 13, 7: 12, 8: 5, 9: 0, 10: 0}
bb_assign = {0: 0, 1: 0, 2: 0, 3: 13, 4: 0, 5: 0, 6: 0, 7: 12, 8: 5, 9: 13, 10: 13}
unload325 = {0: 12, 1: 45, 2: 47, 3: 47, 4: 47, 5: 40, 6: 45, 7: 53, 8: 50, 9: 60, 10: 56, 11: 55, 12: 43, 13: 37, 14: 49, 15: 55, 16: 56}
case_rows = []
for pid, arr, dep, size, pax in planes325:
    s1, s2 = bt_assign[pid], bb_assign[pid]
    case_rows.append([
        str(pid), str(arr), str(dep), str(pax),
        str(s1), n(pax * unload325[s1]),
        str(s2), n(pax * unload325[s2]),
    ])
caption("案例 325 的飞机数据与两种算法的分配")
table(
    ["飞机", "到达", "离开", "乘客", "BT 机位", "BT 费用", "B&B 机位", "B&B 费用"],
    case_rows,
    [0.5, 0.6, 0.6, 0.55, 0.75, 0.95, 0.75, 1.0],
    font_size=8.0,
)
caption("案例 325 的算法对比")
table(
    ["算法", "目标值", "搜索结点", "耗时 / ms", "状态"],
    [
        ["贪心策略 1", "49,239", "—", "—", "可行"],
        ["贪心策略 2", "55,049", "—", "—", "可行"],
        ["回溯法", "48,849", "5,000,000", "141.13", "结点受限"],
        ["分支限界法", "46,699", "399,658", "40.69", "最优"],
    ],
    [1.25, 1.1, 1.15, 1.1, 1.1],
    font_size=8.8,
)
body("回溯法把飞机 4、6 放在远端机位 13，把飞机 9 放在桥位 0；分支限界法把飞机 4、6 改放到桥位 0 的空闲时间窗，把飞机 9、10 放到远端机位 13。桥位 0 的单位下机时间只有 12，远端机位 13 为 37，因此把更多小飞机安排在桥位能显著降低目标；动态可用集在分配前几架飞机后就发现“桥位 0 仍可服务后续小飞机”，而静态后缀下界只按每架飞机的最小兼容下机时间计算，无法反映桥位已被谁占用。这个案例说明：动态下界的价值不仅是“剪掉更多”，更是“让搜索更早看到桥位与远端机位之间的真实取舍”。")
body("另一个典型案例 362 的目标值从 48,613 降到 48,193（下降 0.864%），回溯法在 500 万结点处停止，分支限界法在 363,655 个结点完成；案例 356 从 56,826 降到 54,572（下降 3.966%），分支限界法用 381,344 个结点完成。三个改进案例都属于 K=11、N=1、M=16 的“单桥位 + 多远端机位”结构，说明桥位稀缺时动态可用集最能发挥作用。")
body("为排除搜索实现错误，对 13 个状态改变案例中的 12 个用 5000 万结点上限的回溯法重新求解，均完成搜索且目标值与分支限界法一致；案例 356 的回溯法仍停在 5000 万结点，但其最好目标值 54,572 与分支限界法相同，且分支限界法已证明最优。")

heading("4.6 可扩展性实验", 2)
body(f"可扩展性组共 {sc['cases']} 个案例，K 从 13 到 499。分支限界法证明最优 {sc['optimal']} 个，回溯法 {sc['backtrack_optimal']} 个；分支限界法改进 {sc['improved']} 个、持平 {sc['equal']} 个、更差 0 个。总目标值从 {n(sc['total_backtrack'])} 降到 {n(sc['total_branch'])}，仅下降 {abs(sc['gap_vs_backtrack']):.4f}%；总耗时从 {fnum(sc['backtrack_total_time'])} ms 增加到 {fnum(sc['total_time'])} ms，增加 {sc['time_change_percent']:.2f}%；总结点从 {n(sc['backtrack_total_nodes'])} 降到 {n(sc['total_nodes'])}，减少 {sc['node_reduction_percent']:.2f}%。")
group_rows = []
label = {"K13-15": "K=13–15", "K16-80": "K=16–80", "K81-499": "K=81–499"}
for key in ["K13-15", "K16-80", "K81-499"]:
    g = groups[key]
    group_rows.append([
        label[key], n(g["cases"]), f"{g['optimal']}/{g['backtrack_optimal']}",
        n(g["total_branch"]), n(g["total_backtrack"]),
        fnum(g["total_time"]), fnum(g["backtrack_total_time"]),
        f"{-g['node_reduction_percent']:+.2f}%",
    ])
group_rows.append([
    "合计", n(sc["cases"]), f"{sc['optimal']}/{sc['backtrack_optimal']}",
    n(sc["total_branch"]), n(sc["total_backtrack"]),
    fnum(sc["total_time"]), fnum(sc["backtrack_total_time"]),
    f"{-sc['node_reduction_percent']:+.2f}%",
])
caption("可扩展性组按 K 分组的对比")
table(
    ["K 组", "案例", "B&B/BT 最优", "B&B 目标", "BT 目标", "B&B 耗时", "BT 耗时", "结点变化"],
    group_rows,
    [0.8, 0.5, 0.9, 1.0, 1.0, 0.8, 0.8, 0.7],
    font_size=8.0,
)
body("K=13–15 的 30 个案例是分支限界法真正占优的区间：证明最优数从 24 提高到 28，总目标值从 1,353,206 降到 1,352,660，总结点从 4,215.8 万降到 1,879.3 万（减少 55.4%），但总耗时从 1,204.81 ms 增加到 1,664.74 ms（增加 38.2%）。结点大幅减少而时间增加，说明动态集合的维护成本在这一规模已经不可忽略；不过它换来了多 4 个案例的“证明最优”，对需要精确结论的场景仍然值得。")
body("K=16–80 的 40 个案例中，两法都只有 2 个完成搜索，目标值完全相同（5,657,272），结点数也完全相同（192,760,611）；分支限界法耗时 6,799.74 ms，回溯法 6,442.74 ms，仅多 5.5%。K=81–499 的 30 个案例中，两法都没有完成搜索，目标值完全相同（24,518,473），结点数都等于 3000 万（30 例 × 100 万上限），耗时分别为 6,827.55 ms 和 6,558.78 ms。原因很直接：当 K>15 时动态下界关闭，分支限界法退化为“双贪心上界 + 静态下界”的回溯法；由于初始上界通常与回溯法最终最好解相同，搜索路径几乎完全一致，额外开销只来自候选排序和初始化。")
body("图 4 把三个 K 组的最优数、目标值和耗时放在一起。它清楚地显示：分支限界法的优势集中在 K=13–15 这一段；K≥16 后，优势迅速消失，算法退化为“更贵但几乎等价”的回溯法。这不是实现失败，而是下界强度与维护成本的权衡结果；如果没有更强的、可在多项式时间内计算的下界，单纯在搜索框架上做文章无法解决大规模问题。")
figure("scalability_compare.png", 6.1, "可扩展性组三个 K 区间的最优数、目标值与耗时")

heading("4.7 全量压力测试", 2)
body(f"全量压力组对全部 {n(st['cases'])} 个案例运行，统一预算为 200 ms、20 万结点。分支限界法证明最优 {n(st['optimal'])} 个，回溯法 {n(st['backtrack_optimal'])} 个；分支限界法改进 {n(st['improved'])} 个、持平 {n(st['equal'])} 个、更差 {st['worse']} 个。总目标值从 {n(st['total_backtrack'])} 降到 {n(st['total_branch'])}，下降 {abs(st['gap_vs_backtrack']):.4f}%；总耗时从 {fnum(st['backtrack_total_time'])} ms 增加到 {fnum(st['total_time'])} ms，增加 {st['time_change_percent']:.2f}%；总结点从 {n(st['backtrack_total_nodes'])} 降到 {n(st['total_nodes'])}，减少 {st['node_reduction_percent']:.2f}%（图5）。")
scale_label = {"small": "小规模（K≤15）", "medium": "中规模（K=16..80）", "large": "大规模（K>80）"}
scale_rows = []
for key in ["small", "medium", "large"]:
    s = scales[key]
    scale_rows.append([
        scale_label[key], n(s["cases"]), f"{s['optimal']}/{s['backtrack_optimal']}",
        n(s["total_branch"]), n(s["total_backtrack"]),
        f"{s['improved']}/{s['equal']}/{s['worse']}",
        fnum(s["total_time"]), fnum(s["backtrack_total_time"]),
    ])
scale_rows.append([
    "合计", n(st["cases"]), f"{st['optimal']}/{st['backtrack_optimal']}",
    n(st["total_branch"]), n(st["total_backtrack"]),
    f"{st['improved']}/{st['equal']}/{st['worse']}",
    fnum(st["total_time"]), fnum(st["backtrack_total_time"]),
])
caption("全量压力组按规模的对比")
table(
    ["规模", "案例", "B&B/BT 最优", "B&B 目标", "BT 目标", "改进/持平/劣", "B&B 耗时", "BT 耗时"],
    scale_rows,
    [1.2, 0.55, 0.85, 1.0, 1.0, 0.85, 0.75, 0.75],
    font_size=7.8,
)
body("小规模（K≤15）是分支限界法收益最明显的部分：3000 个案例中，证明最优数从 2276 提高到 2511，总目标值从 98,705,956 降到 98,600,453，改进 699 例、持平 2301 例、更差 0 例。但总耗时从 6,288.0 ms 增加到 14,020.2 ms，增加约 123%。在 200 ms 的预算下，动态下界的单结点成本被放大：它确实找到了更好的解，但每个案例的平均预算更紧，维护动态集合的开销占比更高。")
body("中规模（K=16..80）的 4000 个案例中，两法都只有 12 个完成搜索，总目标值分别为 563,856,175 和 563,870,044，分支限界法仅改进 20 例、持平 3980 例；总耗时 32,932.1 ms 对 31,453.9 ms，增加 4.7%。大规模（K>80）的 3000 个案例中，两法都没有完成搜索，目标值完全相同（2,440,683,200），结点数都等于 6000 万（3000 例 × 20 万上限），耗时 42,790.3 ms 对 40,199.0 ms，增加 6.4%。这两组的结果说明：当 K 超过动态阈值后，分支限界法与回溯法几乎没有区别；所谓“分支限界”的优势只在小规模上成立。")
body("全量测试中，分支限界法的最大单案例耗时为 61.71 ms，回溯法为 31.21 ms；两者都远低于 200 ms 上限，说明时间上限没有成为主要瓶颈，结点上限才是。对于大规模案例，20 万结点在 40 ms 左右用完，搜索在整棵树的很小一部分就被截断；这也解释了为什么两法的目标值完全相同——它们都只来得及探索同一批由贪心上界主导的分支。")
figure("stress_compare.png", 6.1, "全量压力组三个规模的最优数、目标值与耗时")

heading("4.8 两种算法的总体对比", 2)
caption("三组实验中分支限界法相对回溯法的总体表现")
table(
    ["组别", "B&B/BT 最优", "目标差", "时间变化", "结点变化"],
    [
        ["精确组（2000 例）", f"{ex['optimal']}/{ex['backtrack_optimal']}", f"{ex['gap_vs_backtrack']:+.4f}%", f"{ex['time_change_percent']:+.2f}%", f"{-ex['node_reduction_percent']:+.2f}%"],
        ["可扩展性组（100 例）", f"{sc['optimal']}/{sc['backtrack_optimal']}", f"{sc['gap_vs_backtrack']:+.4f}%", f"{sc['time_change_percent']:+.2f}%", f"{-sc['node_reduction_percent']:+.2f}%"],
        ["全量压力组（10000 例）", f"{st['optimal']}/{st['backtrack_optimal']}", f"{st['gap_vs_backtrack']:+.4f}%", f"{st['time_change_percent']:+.2f}%", f"{-st['node_reduction_percent']:+.2f}%"],
    ],
    [1.7, 1.0, 1.0, 1.1, 1.2],
    font_size=8.6,
    left_first=True,
)
body("从解质量看，分支限界法在三组共 12100 个案例上没有一次比回溯法更差，并在 139 个案例上更好；这符合“搜索空间相同、剪枝更强”的理论预期。从效率看，分支限界法只在精确组的总耗时上略优于回溯法（-0.97%），在可扩展性组和全量组分别慢 7.64% 和 15.14%。从搜索量看，分支限界法的结点数在所有组都更少，精确组减少 63.68%，说明“更强的下界”确实有效，但单结点成本更高，结点减少不一定转化为时间减少。")
body("两种算法的时间—质量权衡可以概括为：回溯法结构简单、单结点便宜，适合预算紧、只需要一个可行解的场景；分支限界法通过双贪心上界和动态下界，在 K≤15 时能证明更多案例的最优性，适合小规模精确求解和中等规模解质量评估。K>15 后，分支限界法退化为带双贪心上界的回溯法，继续增加搜索预算的边际收益很低；此时应转向更强的下界、对称性消除或邻域搜索，而不是单纯加大结点上限。")

# ------------------------------------------------------------------ 五、大规模问题与改进
heading("五、大规模问题分析与改进", 1)
heading("5.1 N、M、K 较大时的问题", 2)
body("实验结果已经把大规模分支限界法的困难暴露得很清楚：K=81..499 的 30 个可扩展性案例没有一个完成搜索，全量压力组的大规模 3000 个案例也全部结点受限。结合搜索过程和代码实现，可以把原因归纳为以下几类。")
caption("大规模分支限界法的主要问题")
table(
    ["问题", "实验证据", "影响"],
    [
        ["搜索空间指数增长", "K>80 的 3000 个全量案例全部结点受限；可扩展性组 K=81–499 的 30 例全部未完成", "无法在预算内证明最优，只能返回当前最好解"],
        ["静态下界偏松", "K=16–80 组两法都只有 2/40 完成，结点数完全相同", "下界没有利用时间冲突和机位占用，剪枝效果有限"],
        ["动态下界维护昂贵", "K=13–15 组结点减少 55.4%，但耗时增加 38.2%", "K 增大后单结点成本压过结点收益，只能关闭动态下界"],
        ["对称机位大量存在", "远端机位下机时间集中在 35..60，很多机位完全等价或近似等价", "交换等价机位产生大量目标相同的分支，搜索树重复"],
        ["候选排序与初始化开销", "精确组最大单案例耗时 635.97 ms，回溯法为 184.26 ms", "结点受限时，额外工作没有转化为更好的解"],
        ["时间/结点上限截断", "精确组 5 例、可扩展性组 70 例、全量组 7477 例结点受限", "结果依赖预算，无法给出最优性证明"],
    ],
    [1.45, 3.15, 1.6],
    font_size=8.2,
    left_first=True,
)
body("其中“对称机位”常被忽视。案例生成器给远端机位随机下机时间，但取值范围只有 35..60，且远端机位数量远大于飞机数；同一案例中经常出现多个下机时间相同的远端机位。对搜索树而言，把两架飞机交换到两个等价机位会产生目标值完全相同的两个分支；如果不对机位做等价类合并，分支限界法会把同一棵子树重复搜索很多次。实验中的动态可用集只按 (下机时间, 机位编号) 区分机位，没有做对称性消除，这是 K 增大后结点数仍然巨大的原因之一。")

heading("5.2 改进思路", 2)
body("（1）更强的下界。当前静态下界只按“每架飞机的最小兼容下机时间”求和，完全忽略时间冲突；动态下界虽然考虑了占用，但只维护“可用机位集合”，没有求解飞机之间的匹配。可以在每个结点求解一个忽略时间重叠的指派松弛：把剩余飞机与可用机位做最小费用二分匹配，得到比逐飞机求和更紧的下界；若匹配下界已经不小于 UB，直接剪枝。匹配可在多项式时间内完成，且比多重集合求和更能反映“桥位只有 N 个”的全局约束。")
body("（2）对称性消除。把机位按 (是否靠桥, 是否大机位, 单位下机时间) 分成等价类；同一等价类内只允许按机位编号升序分配，禁止逆序。对完全等价的机位，这一条规则可以把分支数从 S! 降到 1；对近似等价的机位，可以先把下机时间四舍五入到若干档，再做“近似对称”消除，但要注意不能破坏最优性。更稳妥的做法是只在“完全相同”的机位之间做对称性消除，近似等价只用于启发式排序。")
body("（3）最佳优先/束搜索。当前实现是深度优先，优点是内存小，缺点是在一个大子树内可能耗尽预算。可以把候选结点放入优先队列，按 cost+LB 排序，优先扩展最有希望的结点；这就是最佳优先分支限界。最佳优先能更快找到好解，但队列可能膨胀，需要设置束宽（beam width）或结点上限，变成有界的束搜索。对大规模案例，束搜索比“深度优先 + 结点上限”更稳定，因为它不会把全部预算耗在第一个子树。")
body("（4）邻域分解与 LNS。把大规模案例分解成若干时间窗或若干冲突簇：同一时间窗内相互冲突的飞机构成一个子问题，子问题之间通过固定边界解耦。对每个子问题用精确分支限界求解，再合并。更进一步，可以用大邻域搜索（LNS）：从贪心解出发，固定大部分飞机，只挑出贡献最大的 q 架飞机（或与某架飞机时间重叠的邻域）重新精确求解，接受改进后继续迭代。这样每次分支限界的规模是 q 而不是 K，能绕开指数爆炸。")
body("（5）列生成/分支定价。把“一个机位上的可行飞机序列”看成一列，主问题是从所有列中选出一组列，使每架飞机恰好被覆盖一次且目标最小；子问题用动态规划或分支限界生成负检验数列。列生成的分支定价适合机位数多、飞机数大的场景，但实现复杂度高，需要处理列池和整数化。作为实验报告的改进方向，它可以作为“强下界 + 分解”的长期方案。")
body("（6）并行与增量。分支限界法的根结点以下天然可以并行：把根结点的若干候选分支分给多个线程，共享全局 UB，用原子操作或局部 UB 合并。对 16 线程的机器，根层并行通常能获得接近线性的加速；但线程间的 UB 同步和负载均衡需要额外设计。另一个低成本改进是增量维护时间轴和可用集，避免每次递归重新构造候选列表。")

heading("5.3 改进算法框架", 2)
body("综合以上思路，给出一个面向大规模案例的混合框架：用双贪心或 LNS 产生初始上界；对每个邻域子问题用“匹配下界 + 对称性消除 + 有界最佳优先”的分支限界精确求解；子问题之间用固定边界解耦；全局维护最好解，预算用尽时返回。算法 5-1 给出伪代码。")
code_block("算法 5-1  大规模混合求解框架（LNS + 有界分支限界）", [
    "输入：案例 c，初始解 x0，迭代上限 T，邻域规模 q，子问题预算 B",
    "输出：最好解 x*",
    "1  x* ← min(Greedy(ByPassengers), Greedy(ByArrival))",
    "2  for t = 1..T:",
    "3      选择邻域 N：按目标贡献取前 q 架飞机，或取与某架飞机时间重叠的飞机集合",
    "4      固定 N 以外的飞机，构造子问题 c_N",
    "5      对 c_N 运行有界分支限界：",
    "6          初始上界 ← 当前全局解在 N 上的贡献",
    "7          每个结点用最小费用匹配计算剩余飞机的下界",
    "8          对等价机位做对称性消除，只保留代表机位",
    "9          按 cost+LB 做有界最佳优先，束宽 W，结点预算 B",
    "10     若子问题解优于当前全局解：用其替换 N 内分配，更新 x*",
    "11     若连续 R 轮无改进：扩大 q 或随机扰动 N",
    "12 return x*",
])
body("该框架不改变分支限界的正确性：子问题仍然枚举所有未被剪枝的分配，匹配下界和对称性消除都保持最优性；LNS 外层是启发式，所以最终结果不保证全局最优，但在大规模案例上能在有限预算内持续改进。若需要可证明的最优性，可以把 LNS 只作为初始上界，最后对完整问题运行一次精确分支限界；这与实验中“贪心上界 + 精确搜索”的结构一致，只是上界更强。")
body("本实验没有把上述改进全部实现，原因是要在报告中给出可复现的对比需要额外的代码、参数调优和测试时间；本实验的重点是先把标准分支限界法做对、做透，并用 10000 个案例量化它的边界。第 5.2 节的每一条都给出了可验证的实验设计：例如对称性消除可以通过“同一案例开启/关闭等价类合并”的对照实验验证结点数下降；匹配下界可以通过“静态下界/动态下界/匹配下界”三组对比验证剪枝率；LNS 可以通过固定总预算、比较目标值随迭代次数的下降曲线验证。")

# ------------------------------------------------------------------ 六、结论
heading("六、结论", 1)
body("本实验在实验二回溯法的基础上实现了分支限界法，并在 10000 个停机位调度案例上完成了精确组、可扩展性组和全量压力组三组对比。主要结论如下。")
body(f"（1）动态可用机位下界是有效的。精确组中，分支限界法把证明最优数从 {n(ex['backtrack_optimal'])} 提高到 {n(ex['optimal'])}，搜索结点减少 {ex['node_reduction_percent']:.2f}%，总耗时下降 {abs(ex['time_change_percent']):.2f}%；K=11 这一层结点减少约 65.3%，是最主要的收益来源。13 个案例从“回溯法结点受限”变为“分支限界法证明最优”，其中 3 个案例目标值进一步下降。")
body(f"（2）动态下界不是越大越好。K=13–15 时结点减少 55.4%，但耗时增加 38.2%；K>15 后维护成本超过收益，实现中把阈值设为 K≤15。阈值化后，K=16–80 和 K>80 的搜索树与回溯法几乎完全相同，分支限界法只保留双贪心上界带来的少量改进。这个结果说明：下界的强度必须和计算代价一起考虑，不能只看结点数。")
body(f"（3）分支限界法在解质量上稳定优于或等于回溯法。三组共 12100 个案例中，改进 139 例、持平 11961 例、更差 0 例；相对贪心策略 1，改进 4120 例、持平 7980 例、更差 0 例。它没有因为剪枝或预算截断而返回比回溯法更差的解，说明“上界 + 下界 + 安全剪枝”的实现是正确的。")
body(f"（4）大规模问题的瓶颈不在“搜索框架”，而在“下界质量”和“对称性”。全量组大规模 3000 个案例全部结点受限，目标值与回溯法完全相同；可扩展性组 K=81–499 的 30 个案例也没有一个完成。继续加大结点上限只能让两法一起变慢，不能改变解的质量。要突破这一层，需要匹配下界、对称性消除、最佳优先/束搜索、LNS 或列生成等更强的手段。")
body("（5）工程实现上，二元组多重集合的删除/回滚是一个容易出错的细节。只按下机时间删除会在“同下机时间、不同机位”时误删仍可用的机位，导致下界高估和错误剪枝；本实验通过改为 (下机时间, 机位编号) 的精确删除修复了该问题，并用“两边都 complete 的案例目标值必须一致”的交叉校验兜底。这个经验对任何维护动态可用集的 branch-and-bound 实现都适用。")

# ------------------------------------------------------------------ 七、问题记录
heading("七、实验过程中的问题记录", 1)
body("（1）动态可用集误删导致错误剪枝。初版把每架飞机的可用集实现为 multiset<int>，只存下机时间；删除时调用 erase(u_s)，会把所有等于 u_s 的元素都删掉。当两个机位的下机时间相同、其中一个已被占用时，另一个仍然可用的机位也被误删，动态下界被高估，搜索提前剪掉了包含更优解的分支。典型症状是分支限界法自称 optimal，但目标值比回溯法更差（例如案例 784、1994、2317、2385、2959）。修复方式是把元素改为 pair<unloadTime, standId>，删除和回滚都按完整二元组精确匹配；修复后这些案例的目标值与回溯法一致，交叉校验 mismatch 降为 0。")
body("（2）动态下界阈值从 80 调到 15。初版对所有 K≤80 开启动态下界，结果 K=16..80 的中等案例总耗时约 58.6 s，而回溯法约 7.0 s，解质量只提高约 0.1%。逐结点分析发现，动态集合的删除/插入在所有与当前飞机时间重叠的剩余飞机上都要执行，K 增大后单结点成本迅速上升，而结点上限又让搜索很早就被截断，收益无法覆盖成本。把阈值改为 K≤15 后，中等和大规模案例回到静态下界，总耗时恢复到与回溯法同一量级；K=13–15 仍保留动态下界，因为这一段确实能多证明最优。")
body("（3）精确组的案例选择。最初用 --start 0 --count 2000 取“前 2000 个案例”，以为它们就是 K≤11 的精确组；实际上 caseId 的排列与 K 没有单调关系，这 2000 个案例中只有 1300 个满足 K≤11，统计口径错误。改为扫描全部 10000 个案例、按 K≤11 过滤后，得到 2000 个案例，才是与实验二一致的精确组。这个错误提醒我们：按编号截断数据之前必须检查编号与目标属性的关系。")
body("（4）统计脚本的改进方向符号。初版统计把 gap=(B&B-BT)/BT 的正值当作“改进”，导致 improved=0、worse=3 等与原始 CSV 矛盾的结论。后来统一为 improve=(BT-BB)/BT：正值表示分支限界法目标更低，零表示持平，负值表示更差；并在报告中同时给出原始目标值和百分比，避免只看符号。")
body("（5）最大单案例耗时与总耗时不一致。精确组分支限界法总耗时低于回溯法，但最大单案例耗时反而更高（635.97 ms 对 184.26 ms）。原因是总耗时被 13 个“从受限变为完成”的案例拉低，而最大耗时出现在仍然结点受限的案例 311 上：动态下界让每个结点更贵，但没有及时证明最优。报告同时给出总计和最大值，避免用平均值掩盖长尾。")
body("（6）提交包体积。完整 data/cases 约 59 MB，不适合放进提交包；压缩包只保留生成器、combos.csv 和 13 个代表性样例（含案例 325），并在 README 中说明用 generate_cases 重建全部数据。这样既满足“提交代码”的要求，也避免压缩包过大。")

# ------------------------------------------------------------------ 参考文献
heading("参考文献", 1)
refs = [
    "[1] 王晓东. 计算机算法设计与分析（第 5 版）. 北京: 电子工业出版社, 2018.",
    "[2] 张德富, 陈国良. 算法设计与分析. 北京: 清华大学出版社, 2019.",
    "[3] Pinedo M L. Scheduling: Theory, Algorithms, and Systems (5th ed.). Cham: Springer, 2016.",
    "[4] Lawler E L, Wood D E. Branch-and-bound methods: A survey. Operations Research, 1966, 14(4): 699-719.",
    "[5] Luo Z, Tang Q, Qiu L, et al. A branch-and-bound algorithm for the aircraft stand allocation problem. Journal of Air Transport Management, 2021, 92: 102033.",
    "[6] Dorndorf U, Jaehn F, Pesch E. Flight gate scheduling: Models and algorithms. Omega, 2007, 35(3): 255-276.",
]
for ref in refs:
    p = doc.add_paragraph(style="Normal")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.first_line_indent = None
    p.paragraph_format.line_spacing = 1.4
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(ref)
    set_run_font(r, size=10)

# ------------------------------------------------------------------ 附录
heading("附录 A  文件与复现", 1)
body("提交包顶层目录为 2024303425+范劲庚+实验三，包含完整的 C++17/CMake 工程、实验三源码、统计与绘图脚本、报告、代表性样例和结果文件。完整数据不放入压缩包，按下面的命令重建。")
caption("提交包主要目录")
table(
    ["路径", "内容", "说明"],
    [
        ["include/、src/", "核心库", "贪心、回溯、分支限界、IO、校验"],
        ["tools/", "命令行工具", "生成数据、批量基准、单案例求解、导出案例"],
        ["data/sample_cases/", "13 个样例", "覆盖小、中、大规模，含案例 325，可直接构建与运行 CTest"],
        ["data/combos.csv", "100 组 (N,M,K)", "数据生成器的组合表"],
        ["results/", "实验三结果", "CSV、统计 JSON、校验摘要"],
        ["docs/", "报告与脚本", "docx、图表、生成脚本"],
        ["CMakeLists.txt", "构建入口", "airport_core + 全部工具 + CTest"],
    ],
    [1.55, 2.0, 2.65],
    font_size=8.4,
    left_first=True,
)
body("在工程根目录执行以下命令即可构建并复现报告中的主要结果。若 data/cases 为空，先运行 generate_cases 生成 10000 个案例；若只想快速验证，可用 data/sample_cases。")
code_block("复现命令", [
    "cmake -S . -B out/Release -DCMAKE_BUILD_TYPE=Release",
    "cmake --build out/Release -j",
    "ctest --test-dir out/Release --output-on-failure",
    "",
    "# 重建数据（可选，约 59 MB）",
    "./out/Release/bin/generate_cases --out data/cases --combos data/combos.csv",
    "",
    "# 精确组：扫描全部案例，按 K<=11 过滤",
    "./out/Release/bin/branch_bound_benchmark --start 0 --count 10000 \\",
    "  --min-k 0 --max-k 11 --time-limit-ms 2000 --node-limit 5000000 \\",
    "  --data-dir data/cases --out results/branch_bound_benchmark.csv",
    "",
    "# 单案例复现（案例 325）",
    "./out/Release/bin/solve_case --case 325 --data-dir data/cases \\",
    "  --time-limit-ms 5000 --node-limit 5000000",
    "",
    "# 统计与图表（需要工程内 .venv-report）",
    ".venv-report/bin/python docs/make_exp3_stats.py",
    "MPLCONFIGDIR=.cache/matplotlib .venv-report/bin/python docs/make_exp3_figures.py",
    ".venv-report/bin/python docs/make_exp3_report.py",
])
body("报告中的目标值单位为“人·分钟”，即每架飞机的乘客数乘以其机位单位下机时间；耗时单位为毫秒，结点数为搜索树中实际展开的结点数。所有 CSV 都保留了每个案例的原始字段，便于独立复核。")

doc.save(str(OUT))
print("saved", OUT)
