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
OUT = DOCS / "2024303425-范劲庚-实验二报告.docx"

with open(ROOT / "results" / "backtracking_stats.json", encoding="utf-8") as f:
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
hr = hp.add_run("算法分析与设计综合实验（二）")
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
r = p.add_run("实验二  停机位调度问题")
set_run_font(r, size=18, bold=True)
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("——回溯法求解与贪心对比")
set_run_font(r, size=14, bold=False)
for _ in range(3):
    doc.add_paragraph()

cover = doc.add_table(rows=6, cols=2)
cover.alignment = WD_TABLE_ALIGNMENT.CENTER
cover.autofit = False
cover.allow_autofit = False
cover_values = [
    ("课程名称：", "算法分析与设计"),
    ("实验名称：", "停机位调度问题（实验二）"),
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
body("停机位调度是机场运行管理中的核心组合优化问题。本实验在实验一两种贪心策略的基础上，实现回溯法求解停机位分配：以贪心策略 1 的可行解作为初始上界，按“大飞机优先、可选机位少优先、乘客数降序”确定飞机顺序；每个机位用有序区间集合维护半开时间轴；用“剩余飞机乘客数乘以其兼容机位最小下机时间”的后缀和作为宽松下界，在深度优先搜索中进行上界剪枝和下界剪枝。针对大规模案例不可能在有限时间内完成搜索的问题，算法同时设置结点与时间上限，超限时返回当前最好的可行解，并用 Complete 标志区分“已证明最优”和“仅得到可行解”。")
body(f"实验在 10000 个案例上设置三组测试。精确/近精确组取 K≤11 的 {n(ex['cases'])} 个案例，在 1000 万结点、2 s 上限下，{n(ex['optimal'])} 个案例完成搜索并证明最优，{ex['node_limit']} 个案例达到结点上限；回溯法在 {ex['improved']} 个案例中改进贪心，{ex['equal']} 个持平，{ex['worse']} 个更差，总目标值由 {n(ex['total_greedy'])} 降至 {n(ex['total_backtrack'])}，下降 {abs(ex['gap']):.3f}%。可扩展性抽样取 K=13..499 的 {sc['cases']} 个案例，只有 {sc['optimal']} 个完成搜索，{sc['node_limit']} 个达到 500 万结点上限；K=13-15 时仍有 24/30 个案例完成搜索，K=16-80 降为 2/40，K=81-499 为 0/30。全量压力测试覆盖全部 {st['cases']} 个案例，在 20 万结点、200 ms 上限下全部返回可行解，{n(st['optimal'])} 个案例证明最优，{n(st['improved'])} 个案例改进贪心，总目标值下降 {abs(st['gap']):.3f}%。")
body("实验表明：回溯法能够在中小规模上量化贪心解与最优解的差距，并给出可验证的最优解；但当 N、M、K 较大时，搜索树的指数增长、较弱的下界以及大量对称机位使“证明最优”成为主要瓶颈。实际应用应采用“贪心上界 + 更强下界 + 对称性消除 + 分解/束搜索”的混合策略，并把回溯法定位为小规模精确求解和较大规模解质量评估的工具。")
p = doc.add_paragraph(style="Normal")
p.paragraph_format.first_line_indent = None
p.paragraph_format.line_spacing = 1.5
p.paragraph_format.space_before = Pt(8)
r = p.add_run("关键词：停机位调度；回溯法；深度优先搜索；分支剪枝；贪心算法；组合优化")
set_run_font(r, size=11, bold=True)
doc.add_page_break()

# ------------------------------------------------------------------ 一、问题描述
heading("一、问题描述", 1)
heading("1.1 问题背景", 2)
body("航空运输的地面保障效率在很大程度上取决于机场停机位资源的利用水平。靠桥机位直接连接航站楼，旅客下机时间短；远端机位需要摆渡车，旅客下机时间长。给定若干靠桥机位和远端机位，以及若干架飞机的计划到达时刻、计划离开时刻、机型和乘客人数，需要为每架飞机选择一个停靠机位，使全部旅客的下机时间之和最小。")
body("题目假设远端机位数量充足且全部为大机位，远端机位的每人下机时间严格大于靠桥机位；飞机按计划时刻到达和离开；同一架飞机上的旅客下机时间相同，只与所停机位有关。这些假设保证了任意案例都存在可行分配，同时也使目标函数可以写成“乘客数 × 机位下机时间”的线性形式。")
heading("1.2 已知条件与符号", 2)
body("为便于描述，定义如下符号。")
caption("符号说明")
table(
    ["符号", "含义"],
    [
        ["N", "靠桥机位数量"],
        ["M", "远端机位数量"],
        ["S = N + M", "机位总数"],
        ["K", "飞机数量"],
        ["i", "飞机编号，i = 0, 1, …, K-1"],
        ["s", "机位编号，s = 0, 1, …, S-1"],
        ["a_i, d_i", "飞机 i 的计划到达、离开时刻，停靠区间为 [a_i, d_i)"],
        ["p_i", "飞机 i 的乘客人数"],
        ["l_i", "飞机 i 是否为大飞机，1 表示大飞机"],
        ["g_s", "机位 s 是否为大机位，1 表示大机位"],
        ["u_s", "机位 s 的每人下机时间，单位分钟"],
        ["x_{i,s}", "0-1 决策变量，1 表示飞机 i 分配到机位 s"],
        ["F", "总下机时间，单位人·分钟"],
    ],
    [1.3, 4.9], font_size=9, left_first=False,
    align={1: WD_ALIGN_PARAGRAPH.LEFT},
)
body("题目给出的四条基本假设是：远端机位数量足够多且均为大机位；远端机位的下机时间严格大于所有靠桥机位；飞机按计划时刻到达和离开；同一架飞机的旅客下机时间只与机位有关。数据生成时进一步取 M ≥ K，使任意时刻至多 K-1 架飞机占用远端机位，从而至少有一个远端机位空闲，保证可行解一定存在。")
heading("1.3 约束条件与目标函数", 2)
body("每架飞机必须且只能分配到一个机位；大飞机只能停靠大机位，小飞机可以停靠任意机位；同一机位的停靠时间段不能重叠。目标函数为全部旅客下机时间之和。由于同一架飞机上的旅客下机时间相同，飞机 i 若分配到机位 s，其贡献为 p_i · u_s。因此优化模型为：")
formula([
    "min  F = Σ_i p_i · u_{s(i)}",
    "s.t.  Σ_s x_{i,s} = 1,   x_{i,s} ∈ {0, 1}",
    "      若 l_i = 1，则 g_{s(i)} = 1",
    "      若 [a_i, d_i) ∩ [a_j, d_j) ≠ ∅，则 x_{i,s} + x_{j,s} ≤ 1",
])
body("这是一个带机型兼容约束和区间冲突约束的广义分配问题。与普通指派问题相比，机位是否可用取决于已经安排的飞机，决策之间通过时间轴相互影响；与区间图着色问题相比，又增加了机型兼容和目标权重。问题规模较大时，精确求解通常是指数级的。")
heading("1.4 搜索空间与求解难点", 2)
body(f"若不考虑约束，每架飞机有 S 种机位选择，K 架飞机的分配方案最多有 S^K 种；即使利用机型兼容和时间冲突可以排除大量分支，搜索空间仍然随 K 快速增长。本实验的完整数据集包含 100 种 (N, M, K) 组合、每种 100 个案例，K 的范围为 5 到 499，因此必须同时研究小规模精确求解和大规模近似/受限求解。")
body("贪心算法每一步只选择当前下机时间最小的可用机位，时间复杂度低，但可能占用后续高价值飞机更需要的靠桥机位，产生连锁冲突。回溯法可以系统地枚举分配方案，并在搜索完整时证明最优；其难点在于：搜索树的分支因子约为 S，深度为 K；下界如果不考虑时间冲突，往往偏松；大量远端机位具有相同下机时间，产生对称分支。这些因素共同导致大规模案例无法在有限时间内完成搜索。")

# ------------------------------------------------------------------ 二、目的及要求
heading("二、实验目的及要求", 1)
heading("2.1 实验目的", 2)
for text in [
    "掌握将停机位调度问题抽象为带约束组合优化模型的方法，明确决策变量、约束和目标函数。",
    "掌握回溯法的基本框架：深度优先搜索、候选生成、现场保存与恢复、上界与下界剪枝。",
    "设计适合停机位问题的搜索顺序、初始上界、后缀下界和 anytime 终止机制，理解它们对搜索结点数的影响。",
    "通过精确组、可扩展性组和全量压力测试，比较回溯法与贪心法的目标值和运行时间，解释两种算法的适用边界。",
    "分析 N、M、K 较大时回溯法存在的问题，提出可实现的改进算法和工程改进方向。",
]:
    bullet(text)
heading("2.2 实验要求", 2)
body("按照实验指导书，本实验需要完成以下工作：")
for text in [
    "使用实验一生成的 100 种 (N, M, K) 组合、共 10000 个案例，为每个案例计算贪心法和回溯法的总下机时间。",
    "设计回溯法求解停机位分配，给出算法伪代码或流程图，说明搜索顺序、剪枝条件和终止条件。",
    "对比回溯法与贪心法的目标值、改进案例数、运行时间和搜索结点数，分析两种算法的优劣。",
    "分析 N、M、K 较大时回溯法存在的问题，提供改进算法及改进思路。",
    "完成实验报告二，并提交可构建、可复现的源代码和工程文件。",
]:
    bullet(text)
body("本工程对应实验二的回溯法部分。实验一已经实现案例生成、两种贪心策略、统一的数据结构和校验工具；分支限界法和启发式方法属于后续实验，本报告只在第 4.9 节给出改进思路，不在本工程中实现。")
heading("2.3 实验环境", 2)
caption("实验环境")
table(
    ["项目", "配置"],
    [
        ["操作系统", "Arch Linux x86_64"],
        ["处理器", "Intel Core i5-13500H，16 线程"],
        ["内存", "30 GiB"],
        ["编译器", "GCC 16.2.1"],
        ["构建工具", "CMake 4.4.4"],
        ["构建类型", "Release（-O3 -DNDEBUG）"],
        ["编程语言", "C++17"],
        ["数据集", "10000 个二进制案例，另保留 12 个代表性样例"],
    ],
    [1.6, 4.6], font_size=9, left_first=True,
    align={1: WD_ALIGN_PARAGRAPH.LEFT},
)

# ------------------------------------------------------------------ 三、算法设计
heading("三、回溯法设计与实现", 1)
heading("3.1 总体框架与数据结构", 2)
body("回溯法采用“飞机顺序 + 逐层分配”的搜索框架：第 d 层为排序后的第 d 架飞机选择机位，第 K 层得到一个完整分配。程序在 include/solver.h 中扩展了 Solution 结构，增加 complete、timeLimitReached、nodeLimitReached、timeMs 和 nodesExpanded 字段；BacktrackingSolver 的接口与贪心求解器一致，便于在同一个基准程序中替换和比较。")
body("核心搜索类 BacktrackingSearch 位于 src/backtracking.cpp。它为每架飞机预先计算兼容机位数量和最小下机时间，为每个机位维护一个 StandTimeline。StandTimeline 内部使用 std::map<int, int> 保存半开区间 [arrive, depart)，查询时检查新起点的后继是否在区间内、前驱是否覆盖新起点；加入和撤销分别为插入和删除一个键，时间复杂度为 O(log K)。由于每个机位最多同时保存 K 个区间，时间轴的总空间为 O(K + S)。")
body("候选机位在每一层临时生成，结构 Candidate 只保存机位编号和下机时间。搜索过程中 current 数组保存当前部分分配，bestAssign 保存当前最好的完整分配，bestCost 保存对应的目标值。这样的设计避免了在每一层复制整个分配数组，回溯时只需要恢复 current 和被修改的机位时间轴。")
heading("3.2 飞机排序与候选顺序", 2)
body("搜索顺序直接影响能否尽早找到好的可行解，也影响下界剪枝的效果。程序使用 std::stable_sort 按以下优先级排序：")
for text in [
    "大飞机优先：大飞机只能使用大机位，候选集合更小，优先安排可以尽早暴露不可行分支。",
    "兼容机位数少优先：可选机位越少，分支因子越小，先处理可以降低搜索树的宽度。",
    "乘客数降序：乘客数多的飞机对目标值影响大，优先安排有助于尽早得到较小的上界。",
    "飞机编号升序：保证并列情况下结果可复现。",
]:
    bullet(text)
body("在每一层，程序枚举所有满足机型兼容且当前时间轴空闲的机位，并按 unloadTime 升序、机位编号升序排序。先尝试下机时间短的机位，可以更快地得到较好的完整解，从而让上界剪枝更早生效；机位编号作为并列键，保证同一份数据在不同运行中得到相同的搜索顺序。")
heading("3.3 初始上界与后缀下界", 2)
body("算法首先调用贪心策略 1（按乘客数降序）得到一个可行解，并将其目标值作为初始上界 bestCost。这样即使搜索被结点或时间上限中断，返回的也一定是一个可行解；同时，贪心上界通常已经接近最优，可以尽早剪掉大量劣质分支。")
body("为了在搜索早期判断“当前部分分配是否还有可能优于上界”，程序为排序后的飞机计算后缀下界。设 order[d] 为第 d 层要安排的飞机，minUnload[i] 为飞机 i 所有兼容机位中的最小下机时间，则：")
formula([
    "suffixLB[d] = Σ_{j=d}^{K-1} p_{order[j]} · minUnload[order[j]]",
    "suffixLB[K] = 0",
])
body("该下界让每架剩余飞机独立选择兼容机位中下机时间最小的机位，完全忽略时间冲突、机位容量和已占用情况，因此一定不会高于任何完整分配的真实代价，是可采纳（admissible）的下界。它的计算只需要 O(K·S) 的预处理和 O(1) 的查询，但代价是偏松：当靠桥机位已经被占用时，下界仍然按靠桥机位的最小下机时间计算，导致部分分支无法被及时剪掉。")
body("除后缀下界外，程序还使用了两个更直接的剪枝条件：当前部分代价 cost 已经不小于 bestCost 时立即回溯；根结点的后缀下界已经不小于贪心上界时，直接返回贪心解并标记 complete=true，因为此时贪心解已经可以证明最优。")
heading("3.4 深度优先搜索与剪枝", 2)
body("DFS(depth, cost) 首先增加结点计数并检查终止条件。若 depth 等于 K，说明所有飞机都已经分配，此时若 cost 严格小于 bestCost，则更新 bestCost 和 bestAssign。否则，若当前代价或“当前代价 + 后缀下界”已经不可能严格改进上界，则直接返回。通过这两个条件，搜索只保留有希望严格优于当前最好解的分支。")
body("对于当前飞机，程序生成候选机位列表，依次执行：将机位加入时间轴、记录 current、递归到下一层、撤销时间轴、恢复 current。若在递归过程中触发了结点或时间上限，当前层的循环立即停止，避免继续做无效工作。由于每个机位的时间轴使用半开区间，前一架飞机离开时刻等于后一架到达时刻时允许复用同一机位，符合“停靠时间段不能重叠”的题意。")
body("算法 1 给出回溯法的核心伪代码。为了突出主要逻辑，省略了输入输出、异常处理和计时细节。")
code_block("Algorithm 1  Backtracking search for gate assignment", [
    "Input : case C, time limit T, node limit Nmax",
    "Output: best feasible assignment and its objective",
    "",
    "bestCost <- Greedy(ByPassengers, C).objective",
    "bestAssign <- Greedy(ByPassengers, C).assign",
    "order <- stable_sort(planes by large-first, fewer-stands, passengers-desc, id)",
    "for d = K-1 downto 0:",
    "    suffixLB[d] <- suffixLB[d+1] + p[order[d]] * minUnload[order[d]]",
    "",
    "if suffixLB[0] >= bestCost: return (bestAssign, bestCost, complete=true)",
    "",
    "function DFS(depth, cost):",
    "    nodes <- nodes + 1",
    "    if nodes >= Nmax or (nodes mod 1024 == 0 and elapsed >= T):",
    "        mark limit reached; return",
    "    if depth == K:",
    "        if cost < bestCost: bestCost <- cost; bestAssign <- current",
    "        return",
    "    if cost >= bestCost: return",
    "    if cost + suffixLB[depth] >= bestCost: return",
    "",
    "    candidates <- all stands compatible with plane[order[depth]]",
    "                  and available in [arrive, depart)",
    "    sort candidates by (unloadTime, standId) ascending",
    "    for each stand s in candidates:",
    "        current[order[depth]] <- s",
    "        timeline[s].add(arrive, depart)",
    "        DFS(depth + 1, cost + p[order[depth]] * unloadTime[s])",
    "        timeline[s].remove(arrive)",
    "        current[order[depth]] <- -1",
    "        if limit reached: return",
    "",
    "DFS(0, 0)",
    "return (bestAssign, bestCost, complete = not limit reached)",
])
heading("3.5 anytime 机制与结果语义", 2)
body("停机位问题的搜索空间随 K 指数增长，大规模案例不可能在可接受时间内完成枚举。为此，程序提供两个上限：结点上限 nodeLimit 和时间上限 timeLimitMs。结点数在每个 DFS 入口检查；时间每 1024 个结点检查一次，避免频繁读取时钟带来的额外开销。任一上限触发后，搜索立即停止，返回当前最好的可行解，并令 complete=false。")
body("这里必须区分“可行”和“最优”两个概念：feasible 表示每架飞机都得到了满足机型和区间约束的机位；complete 表示搜索已经完整枚举（或在根结点证明贪心解最优），因此返回的目标值可以证明最优。complete=false 的结果仍然是合法可用的，只是不能声称最优。基准程序据此把状态分为 optimal、node_limit、time_limit、infeasible 和 invalid，而不是把所有返回解都当成最优。")
body("由于贪心初始解一定可行，且搜索只在找到严格更优的完整解时更新 bestCost，回溯法返回的目标值不会比贪心策略 1 更差。这一点在三组实验中均得到验证：更差案例数为 0。")
heading("3.6 正确性说明", 2)
body("下面用三个命题说明算法的正确性。")
rich_body([("命题 1（下界可采纳）：", True), ("对任意深度 d 和任意完整分配，若其前 d 层与当前部分分配一致，则真实剩余代价不小于 suffixLB[d]。", False)])
body("证明：suffixLB[d] 对每架剩余飞机分别取兼容机位中的最小下机时间，忽略了时间冲突和机位占用；任何可行完整分配为每架飞机选择的机位下机时间都不小于该最小值，因此剩余代价之和不小于 suffixLB[d]。证毕。")
rich_body([("命题 2（剪枝安全）：", True), ("若当前代价 cost 已经不小于 bestCost，或 cost + suffixLB[d] 不小于 bestCost，则当前子树不可能产生严格优于 bestCost 的完整解。", False)])
body("证明：由命题 1，子树中任意完整解的目标值不小于 cost + suffixLB[d]；若该值不小于 bestCost，则不可能严格改进。当前代价已经不小于 bestCost 时更显然。证毕。")
rich_body([("命题 3（结果正确性）：", True), ("若算法返回 complete=true，则 bestAssign 是全局最优解；若 complete=false，则 bestAssign 是可行解，且其目标值不劣于初始贪心解。", False)])
body("证明：搜索按飞机顺序枚举所有兼容且时间不冲突的机位，剪枝只删除不可能严格改进的分支；当搜索完整结束时，所有可能严格优于当前上界的分支都已被检查，因此 bestCost 是最优值。若触发上限，bestAssign 来自初始贪心解或搜索中已经完整构造的解，故一定可行；更新条件保证它不劣于初始贪心解。证毕。")
heading("3.7 算法流程图", 2)
body("图 1 给出回溯法的整体流程。左侧是预处理和贪心初始上界，右侧是带剪枝和 anytime 终止的深度优先搜索。虚线表示递归返回和上一层继续枚举；当根层搜索结束时，输出 bestAssign 和 complete 标志。")
doc.add_page_break()
figure("flow_backtracking.png", 5.0, "回溯法算法流程图")
doc.add_page_break()
heading("3.8 与贪心算法的关系", 2)
body("从搜索树的角度看，贪心算法只构造了一个完整的叶子：它按固定顺序为每架飞机选择当前下机时间最小的可用机位，不回溯、不比较其他分支。回溯法则以这个叶子为初始上界，系统检查其他可能更优的分支。因此，回溯法的解质量不可能低于作为初始上界的贪心策略 1，但代价是需要额外的搜索时间和空间。")
body("两种算法的差异也决定了它们适合的场景：贪心算法适合大规模在线或快速构造场景，10000 个案例的总耗时约为秒级；回溯法适合小规模离线精确求解、以及作为评估贪心解质量的基准。实验二的核心问题不是“回溯法能否赢贪心”，而是“在多大的规模内可以证明最优，以及超过这个规模后如何退化”。")

# ------------------------------------------------------------------ 四、实验结果
heading("四、实验结果分析", 1)
heading("4.1 实验设置", 2)
body("实验使用实验一生成的 10000 个案例。数据按 (N, M, K) 分为小、中、大三组：小规模 30 种组合，N=1..5、K=5..15；中规模 40 种组合，N=5..20、K=20..80；大规模 30 种组合，N=20..50、K=100..500。每种组合 100 个案例，案例编号连续。机位下机时间、飞机时间段、乘客人数和机型均由固定种子生成，满足题目假设。")
body("为了同时观察精确性、可扩展性和全量可行性，实验设置三组参数，如表 3 所示。精确组只取前 3000 个案例中 K≤11 的 2000 个，以较高的结点和时间上限观察搜索完成情况；可扩展性组按 K 分层抽样 100 个案例；全量压力测试覆盖全部 10000 个案例，用较低的上限模拟实际可接受的计算预算。")
caption("三组实验设置")
table(
    ["实验组", "案例数", "K 范围", "时间上限", "结点上限", "目的"],
    [
        ["精确/近精确组", n(ex["cases"]), "5..11", "2000 ms", n(10000000), "观察最优证明与小规模改进"],
        ["可扩展性抽样", n(sc["cases"]), "13..499", "1000 ms", n(5000000), "观察搜索规模随 K 的增长"],
        ["全量压力测试", n(st["cases"]), "5..499", "200 ms", n(200000), "验证全量可行性与 anytime 行为"],
    ],
    [1.25, 0.7, 0.75, 0.75, 0.95, 1.85], font_size=8.5,
    align={0: WD_ALIGN_PARAGRAPH.LEFT, 5: WD_ALIGN_PARAGRAPH.LEFT},
)
body("所有实验在同一台机器上以 Release 模式运行，计时使用 std::chrono::steady_clock，包含预处理、贪心初始解和搜索过程。案例读取、解合法性检查和目标值重算由基准程序统一完成。具体命令见附录 A。")
heading("4.2 正确性校验", 2)
body("每个案例在运行基准程序时依次执行：validateCase 检查案例参数、机位和飞机数据；贪心策略 1 生成初始解并调用 validateSolution 检查完整分配、机型兼容和时间不重叠；回溯法返回解后再次调用 validateSolution；最后用 calculateObjective 重新计算目标值并与求解器返回值核对。只有非法案例和非法解都为 0 时，基准程序才以成功状态退出。")
caption("三组实验的校验结果")
table(
    ["实验组", "案例数", "非法案例", "非法解", "不可行", "完成/受限", "时间受限"],
    [
        ["精确组", n(ex["cases"]), "0", "0", "0", f"{n(ex['optimal'])}/{ex['node_limit']}", "0"],
        ["可扩展性", n(sc["cases"]), "0", "0", "0", f"{n(sc['optimal'])}/{sc['node_limit']}", "0"],
        ["全量压力", n(st["cases"]), "0", "0", "0", f"{n(st['optimal'])}/{n(st['node_limit'])}", "0"],
    ],
    [1.15, 0.7, 0.8, 0.75, 0.75, 1.25, 0.75], font_size=8.5,
)
body("三组实验均没有非法案例、非法解和不可行解，也没有触发时间上限；所有未完成搜索的案例都是因为结点上限。精确组的 14 个受限案例全部出现在 K=11；可扩展性组的 74 个受限案例分布在中大规模；全量压力测试的 7712 个受限案例覆盖了几乎全部中大规模案例。所有返回解都通过 validateSolution，说明“未证明最优”不等于“不可行”。")
body("完整校验记录见 results/backtracking_validation_summary.txt，逐案例状态见 results/backtracking_benchmark.csv、backtracking_scalability.csv 和 backtracking_stress_all.csv。")
heading("4.3 精确组总体结果", 2)
body(f"精确组共 {n(ex['cases'])} 个案例，其中 K=5 和 K=6 各 400 个，K=7 300 个，K=8 100 个，K=9 500 个，K=10 200 个，K=11 100 个。表 5 汇总了贪心与回溯的总体对比。")
caption("精确组总体对比（K≤11，2000 个案例）")
table(
    ["指标", "贪心策略 1", "回溯法", "说明"],
    [
        ["总目标值", n(ex["total_greedy"]), n(ex["total_backtrack"]), f"减少 {n(ex['total_greedy']-ex['total_backtrack'])}，{pct(ex['gap'])}"],
        ["改进 / 持平 / 更差", "—", f"{ex['improved']} / {ex['equal']} / {ex['worse']}", "回溯不劣于初始贪心"],
        ["完成搜索（证明最优）", "—", f"{n(ex['optimal'])}（{ex['optimal']/ex['cases']*100:.1f}%）", "其余为结点受限"],
        ["结点受限 / 时间受限", "—", f"{ex['node_limit']} / {ex['time_limit']}", "14 个均在 K=11"],
        ["总耗时", "—", f"{fnum(ex['total_time'],3)} ms", f"平均 {fnum(ex['mean_time'],3)} ms"],
        ["最大单案例耗时", "—", f"{fnum(ex['max_time'],3)} ms", "未达到 2 s 上限"],
        ["总结点 / 最大结点", "—", f"{n(ex['total_nodes'])} / {n(ex['max_nodes'])}", "最大结点达到 1000 万"],
        ["改进案例平均改进", "—", f"{ex['improved_mean_gap']:.3f}%", "仅统计 291 个改进案例"],
        ["单案例最大改进", "—", f"{ex['max_gap']:.3f}%", "案例 2081"],
    ],
    [1.35, 1.25, 1.55, 2.0], font_size=8.5,
    align={0: WD_ALIGN_PARAGRAPH.LEFT, 3: WD_ALIGN_PARAGRAPH.LEFT},
)
body(f"在 2000 个案例中，回溯法在 {ex['improved']} 个案例中改进了贪心，占 {ex['improved']/ex['cases']*100:.2f}%；其余 {ex['equal']} 个持平，没有更差。总目标值从 {n(ex['total_greedy'])} 降到 {n(ex['total_backtrack'])}，绝对减少 {n(ex['total_greedy']-ex['total_backtrack'])} 人·分钟，相对下降 {abs(ex['gap']):.3f}%。改进案例的平均改进幅度为 {ex['improved_mean_gap']:.3f}%，单案例最大改进为 {ex['max_gap']:.3f}%。")
body(f"从证明最优的角度看，{n(ex['optimal'])} 个案例完成搜索，占 {ex['optimal']/ex['cases']*100:.1f}%；14 个 K=11 案例在 1000 万结点处停止，占全部案例的 {ex['node_limit']/ex['cases']*100:.1f}%。所有 14 个受限案例仍然返回了可行解，且由于初始上界的存在，它们的目标值不劣于贪心。总搜索结点数为 {n(ex['total_nodes'])}，平均 {fnum(ex['mean_nodes'],1)} 个/案例；总耗时为 {fnum(ex['total_time'],3)} ms，平均 {fnum(ex['mean_time'],3)} ms/案例。")
body("需要强调的是，精确组的目标值下降幅度（0.711%）明显小于实验一中两种贪心策略之间的差异（10.42%）。这说明贪心策略 1 在大多数案例上已经接近最优；回溯法的主要价值在于量化剩余差距、在部分案例中发现更优分配，而不是在所有案例上大幅改写解。")
heading("4.4 精确组按 K 分析", 2)
body("表 6 按 K 给出案例数、完成搜索数、改进数、目标值和平均搜索规模。图 2 进一步展示平均结点数和平均耗时随 K 的变化，图 3 展示改进覆盖率和改进幅度。")
caption("精确组按 K 的统计")
rows = []
for k in ["5", "6", "7", "8", "9", "10", "11"]:
    r = byk[k]
    rows.append([
        k, n(r["cases"]), n(r["optimal"]), n(r["node_limit"]),
        f"{r['improved']}/{r['equal']}", n(r["total_greedy"]), n(r["total_backtrack"]),
        pct(r["gap"]), fnum(r["mean_nodes"], 1), fnum(r["mean_time"], 3),
    ])
rows.append([
    "合计", n(ex["cases"]), n(ex["optimal"]), n(ex["node_limit"]),
    f"{ex['improved']}/{ex['equal']}", n(ex["total_greedy"]), n(ex["total_backtrack"]),
    pct(ex["gap"]), fnum(ex["mean_nodes"], 1), fnum(ex["mean_time"], 3),
])
table(
    ["K", "案例数", "最优", "结点受限", "改进/持平", "贪心目标值", "回溯目标值", "变化", "平均结点", "平均耗时/ms"],
    rows,
    [0.32, 0.5, 0.42, 0.5, 0.58, 0.78, 0.78, 0.62, 0.72, 0.72],
    font_size=7.6,
)
figure("exact_growth.png", 6.2, "精确组平均搜索结点数与平均耗时随 K 的变化")
body("从表 6 和图 2 可以看到，K=5 到 K=8 的搜索规模增长相对温和：平均结点数从 86.9 增至 17,467.7，平均耗时从 0.0038 ms 增至 0.511 ms，所有案例都完成搜索。K=9 平均结点数增至 63,979.2，最大单案例达到 9,106,914 个结点，平均耗时 1.811 ms，最大耗时 251.83 ms；K=10 的平均结点数为 68,889.8，最大 2,280,629，平均耗时 1.893 ms，最大 62.88 ms。K=11 的平均结点数跃升至 2,170,355.7，平均耗时 60.98 ms，14 个案例达到 1000 万结点上限，最大耗时 298.96 ms。")
body("K=9 与 K=10 的平均结点数并非严格单调：K=10 的案例数只有 200 个，且没有出现 K=9 中接近 1000 万结点的极端案例；平均耗时也受案例构成和机器负载影响。因此应结合最大值和分组案例数理解均值，而不能把平均结点数当作严格的增长曲线。")
figure("exact_improvement.png", 6.2, "精确组各 K 的改进覆盖率、总目标值下降和单案例最大改进")
body("图 3 显示，改进覆盖率在 K=5 到 K=8 为 6.0% 到 12.0%，K=9 和 K=10 提高到 23.2% 和 23.5%，K=11 为 18.0%。总目标值下降幅度在 K=9 和 K=10 最大，分别为 1.000% 和 1.085%；K=5 到 K=8 为 0.266% 到 0.616%。这并不能简单解释为“K 越大回溯越有效”，因为不同 K 的案例构成、机位冗余和下机时间分布不同；但它说明在中等规模（K≈9-10）上，贪心的短视仍然会留下可被精确搜索利用的改进空间。")
body("从算法行为看，K≤10 的所有案例都完成了搜索，说明在 1000 万结点上限内，当前的下界和排序策略可以覆盖这些规模；K=11 开始出现结点受限，表明搜索规模已经接近本实验设定的边界。14 个受限案例的平均搜索时间不到 300 ms，远低于 2 s 时间上限，进一步说明瓶颈是结点数而不是时钟。")
heading("4.5 典型案例分析", 2)
body("为了解释回溯法为什么能改进贪心，选取案例 2081（N=2，M=8，K=6）进行逐飞机分析。该案例有 2 个靠桥机位、8 个远端机位；机位 0 为靠桥大机位，下机时间 10 分钟；机位 1 为靠桥小机位，下机时间 15 分钟；远端机位 2..9 的下机时间为 35..51 分钟。6 架飞机的数据如表 7 所示。")
caption("典型案例 2081 的逐飞机分配")
table(
    ["飞机", "时间段", "乘客", "机型", "策略 1（机位/下机/贡献）", "策略 2（机位/下机/贡献）", "回溯（机位/下机/贡献）"],
    [
        ["0", "[743, 908)", "69", "小", "桥1 / 15 / 1035", "桥0 / 10 / 690", "桥0 / 10 / 690"],
        ["1", "[35, 185)", "67", "小", "桥1 / 15 / 1005", "桥0 / 10 / 670", "桥1 / 15 / 1005"],
        ["2", "[613, 723)", "149", "大", "远5 / 35 / 5215", "桥0 / 10 / 1490", "桥0 / 10 / 1490"],
        ["3", "[138, 192)", "68", "小", "桥0 / 10 / 680", "桥1 / 15 / 1020", "桥0 / 10 / 680"],
        ["4", "[631, 797)", "153", "小", "桥0 / 10 / 1530", "桥1 / 15 / 2295", "桥1 / 15 / 2295"],
        ["5", "[246, 311)", "79", "大", "桥0 / 10 / 790", "桥0 / 10 / 790", "桥0 / 10 / 790"],
        ["合计", "—", "—", "—", "10255", "6955", "6950"],
    ],
    [0.55, 1.0, 0.55, 0.5, 1.22, 1.22, 1.22], font_size=8.0,
)
body("策略 1 按乘客数降序处理，先安排乘客 153 的飞机 4，把它放在靠桥机位 0；随后安排乘客 149 的飞机 2，此时桥 0 在 [631, 797) 与飞机 2 的 [613, 723) 冲突，只能把飞机 2 放到远端机位 5。飞机 0 的 [743, 908) 又与飞机 4 在桥 0 冲突，只能使用桥 1。这样，飞机 2 多付了 25 分钟/人，飞机 0 多付了 5 分钟/人，飞机 4 少付了 5 分钟/人，净损失 3305 人·分钟。")
body("回溯法在搜索中把飞机 4 放到桥 1，把飞机 2 和飞机 0 放到桥 0：飞机 2 从远端 35 分钟降到桥 0 的 10 分钟，节省 149×25=3725；飞机 4 从桥 0 的 10 分钟升到桥 1 的 15 分钟，增加 153×5=765；飞机 0 从桥 1 的 15 分钟降到桥 0 的 10 分钟，节省 69×5=345。三项合计净节省 3725-765+345=3305，正好等于 10255-6950。这个案例说明，贪心的单步最优可能造成“机位占用链”，而回溯法通过重新安排后续飞机可以打破这条链。")
body("策略 2 按到达顺序处理，得到 6955，仅比最优值高 5。原因是它把飞机 1 放在桥 0、飞机 3 放在桥 1，而最优解交换了这两架飞机：飞机 1 的乘客数为 67，飞机 3 的乘客数为 68，交换后节省 68×5-67×5=5。这个例子也说明，贪心策略 2 在某些案例上可能优于策略 1；本实验固定用策略 1 作为回溯的初始上界，是为了保证“回溯不劣于基线”，而不是断言策略 1 在所有案例上最好。")
body("回溯法在该案例上只展开 56 个结点，耗时 0.012754 ms，就完成了搜索并证明 6950 最优。小规模案例的搜索开销远小于贪心预处理和程序启动成本，这也是精确组平均耗时只有数毫秒的原因之一。")
heading("4.6 可扩展性实验", 2)
body("精确组只覆盖到 K=11；为了观察搜索规模随 K 的增长，实验按 K 分层抽样 100 个案例：K=13、14、15 各 10 个，K=16..80 每 100 个取 1 个共 40 个，K=81..499 每 100 个取 1 个共 30 个。每组使用 500 万结点、1000 ms 上限。结果如表 8 和图 4 所示。")
caption("可扩展性抽样的分组结果")
rows = []
for g in ["K13-15", "K16-80", "K81-499"]:
    r = groups[g]
    rows.append([
        g, n(r["cases"]), n(r["optimal"]), n(r["node_limit"]),
        f"{r['improved']}/{r['equal']}", n(r["total_greedy"]), n(r["total_backtrack"]),
        pct(r["gap"]), fnum(r["mean_nodes"], 1), fnum(r["mean_time"], 1),
    ])
rows.append([
    "合计", n(sc["cases"]), n(sc["optimal"]), n(sc["node_limit"]),
    f"{sc['improved']}/{sc['equal']}", n(sc["total_greedy"]), n(sc["total_backtrack"]),
    pct(sc["gap"]), fnum(sc["mean_nodes"], 1), fnum(sc["mean_time"], 1),
])
table(
    ["K 分组", "案例数", "最优", "结点受限", "改进/持平", "贪心目标值", "回溯目标值", "变化", "平均结点", "平均耗时/ms"],
    rows,
    [0.62, 0.5, 0.42, 0.5, 0.58, 0.78, 0.78, 0.62, 0.74, 0.74],
    font_size=7.6,
)
figure("scalability_status.png", 6.2, "可扩展性抽样的完成情况、目标值改进和平均耗时")
body(f"K=13-15 的 30 个案例中，24 个完成搜索（80.0%），6 个达到 500 万结点上限；平均结点数 1,405,268，平均耗时 39.4 ms，目标值下降 2.379%。K=16-80 的 40 个案例中，只有 2 个完成搜索（5.0%），38 个受限；平均结点数 4,819,015，平均耗时 158.7 ms，目标值下降 0.483%。K=81-499 的 30 个案例全部受限，平均结点数正好是 5,000,000，平均耗时 217.8 ms，目标值下降 0.088%。")
body(f"总体上，100 个案例中只有 {sc['optimal']} 个完成搜索，{sc['node_limit']} 个达到结点上限；总目标值从 {n(sc['total_greedy'])} 降到 {n(sc['total_backtrack'])}，下降 {abs(sc['gap']):.3f}%。所有案例都没有触发 1000 ms 时间上限，说明在 500 万结点规模下，结点检查先于时间检查生效；平均耗时最高为 217.8 ms，远低于 1 s。")
body("从 K=13-15 到 K=16-80，完成搜索的比例从 80% 骤降到 5%；从 K=16-80 到 K=81-499，完成搜索比例降为 0。这是本实验最重要的可扩展性结论：在当前的排序和下界下，K≈15 是从“多数可证明最优”走向“几乎只能得到可行解”的分界区间。即使 K=81-499 的案例仍然有 7 个改进了贪心，它们也只是搜索早期找到的更好叶子，不能声称最优。")
heading("4.7 全量压力测试", 2)
body("为了验证全部 10000 个案例在有限计算预算下的行为，实验把结点上限降到 20 万、时间上限设为 200 ms，对全部案例运行回溯法。这个设置不代表精确求解，而是模拟“在可接受时间内尽量改进贪心”的 anytime 使用方式。结果如表 9 和图 5 所示。")
caption("全量压力测试按规模统计")
rows = []
for key, label in (("small", "小"), ("medium", "中"), ("large", "大")):
    r = scales[key]
    rows.append([
        label, n(r["cases"]), n(r["optimal"]), n(r["node_limit"]),
        f"{r['improved']}/{r['equal']}", n(r["total_greedy"]), n(r["total_backtrack"]),
        pct(r["gap"]), fnum(r["mean_nodes"], 1), fnum(r["mean_time"], 2),
    ])
rows.append([
    "合计", n(st["cases"]), n(st["optimal"]), n(st["node_limit"]),
    f"{st['improved']}/{st['equal']}", n(st["total_greedy"]), n(st["total_backtrack"]),
    pct(st["gap"]), fnum(st["mean_nodes"], 1), fnum(st["mean_time"], 2),
])
table(
    ["规模", "案例数", "最优", "结点受限", "改进/持平", "贪心目标值", "回溯目标值", "变化", "平均结点", "平均耗时/ms"],
    rows,
    [0.42, 0.55, 0.48, 0.55, 0.62, 0.8, 0.8, 0.62, 0.72, 0.72],
    font_size=7.6,
)
figure("stress_by_scale.png", 6.2, "全量压力测试的完成情况、改进覆盖和平均耗时")
body(f"全部 {n(st['cases'])} 个案例都返回了可行解，非法解、不可行解和时间上限触发均为 0。{n(st['optimal'])} 个案例完成搜索（{st['optimal']/st['cases']*100:.2f}%），{n(st['node_limit'])} 个案例达到 20 万结点上限；回溯在 {n(st['improved'])} 个案例中改进贪心，{n(st['equal'])} 个持平，没有更差。总目标值从 {n(st['total_greedy'])} 降到 {n(st['total_backtrack'])}，下降 {abs(st['gap']):.3f}%，绝对减少 {n(st['total_greedy']-st['total_backtrack'])} 人·分钟。")
body(f"分规模看，小规模 3000 个案例中有 {n(scales['small']['optimal'])} 个完成搜索，改进 {n(scales['small']['improved'])} 个，目标值下降 {abs(scales['small']['gap']):.3f}%；中规模 4000 个案例只有 {scales['medium']['optimal']} 个完成搜索，但改进 {n(scales['medium']['improved'])} 个，目标值下降 {abs(scales['medium']['gap']):.3f}%；大规模 3000 个案例全部受限，仍有 {n(scales['large']['improved'])} 个改进，目标值下降 {abs(scales['large']['gap']):.3f}%。")
body(f"全量压力测试总耗时 {fnum(st['total_time'],1)} ms（约 {st['total_time']/1000:.1f} s），平均 {st['mean_time']:.2f} ms/案例，最大 {st['max_time']:.2f} ms；总搜索结点数 {n(st['total_nodes'])}。与精确组相比，20 万结点上限使中大规模案例几乎全部受限，但仍然能在前 20 万个结点内找到改进解，说明 anytime 机制在实际预算下是有效的。")
heading("4.8 大规模案例中回溯法的问题", 2)
body("综合三组实验，N、M、K 较大时回溯法的问题可以归纳为表 10 的五个方面。它们不是实现细节，而是算法本身的结构性限制。")
caption("大规模回溯法的主要问题")
table(
    ["问题", "实验证据", "后果"],
    [
        ["搜索树指数增长", "K=11 已有 14/100 个案例达到 1000 万结点；K=16-80 仅 2/40 完成搜索", "无法在有限时间内证明最优"],
        ["下界偏松", "后缀下界忽略时间冲突和机位占用；K=11 受限案例仍在 300 ms 内耗尽结点", "大量分支无法被及时剪掉"],
        ["对称机位多", "M 可达 545，远端机位下机时间大量重复或接近", "同一实质分配被重复枚举"],
        ["初始上界已接近最优", "精确组总改进仅 0.711%，改进案例平均 4.80%", "大部分时间用于证明“不能改进”"],
        ["约束耦合强", "桥位占用会沿时间轴连锁影响后续飞机", "局部选择难以用简单下界估计"],
    ],
    [1.2, 3.1, 1.9], font_size=8.5,
    align={0: WD_ALIGN_PARAGRAPH.LEFT, 1: WD_ALIGN_PARAGRAPH.LEFT, 2: WD_ALIGN_PARAGRAPH.LEFT},
)
body("第一，搜索树的宽度约为可用机位数 S=N+M，深度为 K，最坏情况下的叶子数为 S^K。即使机型兼容和时间冲突会剪掉大量分支，K 超过 15 后仍迅速超出预算。第二，当前后缀下界让每架剩余飞机独立选择最小下机时间，忽略了“靠桥机位已被占用”“大飞机只能使用大机位”等耦合信息；在桥位紧张的案例中，下界可能明显低于真实剩余代价，导致剪枝失效。")
body("第三，大量远端机位具有相同或相近的下机时间，交换两架飞机在相同下机时间的机位之间不会改变目标值，但搜索仍会把它们当作不同分支枚举。这种对称性在中大规模案例中尤其严重。第四，贪心策略 1 已经给出了很接近最优的上界，精确组的总改进只有 0.711%，说明搜索的大部分工作不是“找到更好的解”，而是“证明没有更好的解”；在没有强下界的情况下，这项工作本质上是指数级的。")
body("第五，机位占用通过时间轴相互耦合：一架飞机占用桥位，可能迫使后续多架飞机使用远端机位，形成连锁损失。简单的“当前代价”和“剩余飞机独立下界”都难以准确估计这种连锁影响。因此，大规模案例中回溯法往往只能返回“比贪心略好”的可行解，而不能给出最优性证明。")
heading("4.9 改进算法与改进思路", 2)
body("本实验已经实现了四项工程改进：用贪心策略 1 构造初始上界；用后缀下界进行下界剪枝；按大飞机、可选机位少、乘客数降序排序；用结点/时间上限实现 anytime 返回。这些改进使 K≤11 的精确组有 99.3% 的案例完成搜索，并使全量 10000 个案例都能返回可行解。要进一步改善大规模表现，可以从以下方向继续。")
body("（1）更强的下界。当前下界忽略了时间冲突，可以把剩余飞机按时间段划分成若干冲突团，对每个团求解一个忽略机位区分的指派松弛；也可以把“每架飞机至少要占用一个兼容机位的一个时间片”写成线性规划松弛，用其对偶解作为下界。强下界不会改变最坏复杂度，但能显著减少实际搜索结点。")
body("（2）对称性消除。对下机时间相同、机型相同、时间轴等价的远端机位，只保留一个代表，或者在候选排序中规定“等价的已用机位必须按编号连续使用”。这样可以避免同一实质分配被重复枚举，尤其适合 M 很大的案例。")
body("（3）问题分解。可以把靠桥机位和远端机位分开处理：先决定哪些飞机使用靠桥机位，再把剩余飞机分配到远端机位；远端机位之间下机时间差异较小，可以用区间调度或最小费用流求解。也可以按时间窗把飞机分成若干相互弱耦合的组，对每组分别精确求解，再在组间做局部调整。")
body("（4）束搜索（beam search）。把 DFS 改成按层扩展的受限搜索：每层只保留 B 个最有希望的部分状态，用 cost + suffixLB 排序。B 固定时复杂度为 O(B·K·S·log K)，可以在大规模案例上快速得到比贪心更好的解，但不再保证最优。算法 2 给出束搜索的伪代码。")
code_block("Algorithm 2  Beam search over partial assignments", [
    "Input : case C, beam width B, lower bound suffixLB",
    "Output: best feasible assignment",
    "",
    "best <- Greedy(ByPassengers, C)",
    "level <- { empty partial assignment with cost 0 }",
    "for d = 0 to K-1:",
    "    next <- empty",
    "    for each state in level:",
    "        for each stand s compatible with plane[order[d]]:",
    "            if s is available in state.timeline:",
    "                child <- state with plane[order[d]] assigned to s",
    "                if child.cost + suffixLB[d+1] < best.cost:",
    "                    next.add(child)",
    "    keep the B states in next with smallest (cost + suffixLB[d+1])",
    "    level <- next",
    "    if level is empty: break",
    "return best",
])
body("（5）更好的初始上界与局部搜索。可以先运行两种贪心策略并取较优者，再对贪心解做交换、插入、重定位等局部搜索，得到一个更紧的上界；上界越紧，回溯法需要证明的分支越少。对大规模案例，局部搜索本身可能比回溯更有效。")
body("（6）混合与并行。小规模案例使用完整回溯或分支限界证明最优；中等规模使用束搜索或限制差异搜索；大规模使用贪心 + 局部搜索/大邻域搜索。不同子问题或不同初始上界可以在多线程上并行搜索，共享全局上界。")
caption("改进方向与预期效果")
table(
    ["方向", "具体做法", "预期效果", "风险/代价"],
    [
        ["强下界", "时间冲突团、LP/指派松弛、拉格朗日松弛", "减少搜索结点，提升证明最优的规模", "计算下界本身有开销"],
        ["对称性消除", "等价机位合并、编号规范、支配规则", "避免重复枚举，缩小搜索树", "等价判定需谨慎，避免丢失最优解"],
        ["问题分解", "桥位/远端分解、时间窗分组、最小费用流", "把大问题拆成可解子问题", "分解可能损失全局最优性"],
        ["束搜索/LNS", "限制每层宽度、局部破坏重建", "大规模快速改进，时间可控", "不再保证最优"],
        ["更好上界", "两种贪心取优、局部搜索、插入交换", "增强剪枝，减少证明工作", "增加预处理时间"],
        ["混合/并行", "小规模精确、大规模启发式、多线程共享上界", "兼顾质量与规模", "实现复杂，负载均衡困难"],
    ],
    [0.95, 2.0, 1.85, 1.4], font_size=8.3,
    align={0: WD_ALIGN_PARAGRAPH.LEFT, 1: WD_ALIGN_PARAGRAPH.LEFT,
           2: WD_ALIGN_PARAGRAPH.LEFT, 3: WD_ALIGN_PARAGRAPH.LEFT},
)
body("这些改进中，强下界和对称性消除最适合与现有回溯框架结合；问题分解和束搜索更适合大规模场景；局部搜索则可以作为独立的大规模启发式。实验三的分支限界法可以看作“强下界 + 上界剪枝”的延续，实验四的启发式方法可以看作“束搜索/局部搜索”的延续。")

# ------------------------------------------------------------------ 五、复杂度
heading("五、算法时间复杂性分析", 1)
heading("5.1 贪心算法", 2)
body("设机位总数为 S=N+M。贪心算法首先对 K 架飞机排序，时间复杂度为 O(K log K)；对每架飞机扫描 S 个机位，每次用有序时间轴判断可用性，时间为 O(log K)，因此单架飞机的候选筛选为 O(S log K)。总时间复杂度为 O(K log K + K·S·log K)，空间复杂度为 O(K + S)。在本题中 S 最大约 600、K 最大 499，贪心算法在 10000 个案例上的总耗时约为秒级。")
heading("5.2 回溯算法", 2)
body("回溯法的预处理包括兼容机位统计、排序和后缀下界，时间为 O(K·S + K log K)。搜索树的最坏情况有 O(S^K) 个结点；每个结点需要扫描 S 个机位、检查时间轴并进行候选排序，单结点代价为 O(S log K + S log S)。因此最坏时间复杂度为 O(S^K·S·log K)，空间复杂度为 O(K·S + K + S)，其中 O(K·S) 来自每层候选数组，O(K+S) 来自时间轴和当前分配。")
body("实际运行中，上界和下界剪枝会大幅减少结点数，但最坏复杂度仍然是指数级的。若设置结点上限 Nmax，则时间复杂度退化为 O(Nmax·S·log K)，可以在有限预算内返回当前最好解；这正是 anytime 机制的理论依据。")
heading("5.3 实测增长与复杂度解释", 2)
body("表 6 和表 8 的实测数据与指数增长的趋势一致：K=5 时平均只有 86.9 个结点，K=8 时增至 17,467.7，K=11 时增至 2,170,355.7；K=13-15 的平均结点数为 1,405,268，K=16-80 为 4,819,015，K=81-499 则全部达到 500 万上限。搜索时间与结点数近似成正比：精确组平均 3.72 ms，可扩展性组平均 140.6 ms，全量压力组平均 7.98 ms（因为结点上限只有 20 万）。")
caption("各算法的时间与空间复杂度")
table(
    ["算法", "时间复杂度", "空间复杂度", "说明"],
    [
        ["贪心", "O(K log K + K·S·log K)", "O(K + S)", "排序 + 每架飞机扫描机位"],
        ["回溯（最坏）", "O(S^K·S·log K)", "O(K·S + K + S)", "指数搜索，剪枝只改变常数/实际结点数"],
        ["回溯（结点上限）", "O(Nmax·S·log K)", "O(K·S + K + S)", "达到上限后返回当前最好解"],
        ["束搜索（改进）", "O(B·K·S·log K)", "O(B·K + K + S)", "B 为束宽，不再保证最优"],
    ],
    [1.05, 2.0, 1.55, 1.6], font_size=8.5,
    align={0: WD_ALIGN_PARAGRAPH.LEFT, 1: WD_ALIGN_PARAGRAPH.LEFT,
           2: WD_ALIGN_PARAGRAPH.LEFT, 3: WD_ALIGN_PARAGRAPH.LEFT},
)
body("需要强调的是，复杂度分析给出的是最坏情况上界，不能直接解释某个具体案例的运行时间。实际结点数取决于上界质量、下界松紧、飞机排序、机位对称性和案例的时间冲突结构。实验中 K=9 的平均结点数高于 K=10，就是案例构成和极端值造成的；因此报告同时给出平均值、最大值和受限案例数，避免只用单一均值下结论。")

# ------------------------------------------------------------------ 六、总结
heading("六、问题思考与总结", 1)
body("本实验完成了停机位调度问题的回溯法实现、与贪心法的对比、可扩展性分析和改进方案设计，主要结论如下。")
for text in [
    "回溯法可以在小规模上给出可证明的最优解。K≤11 的 2000 个案例中，1986 个完成搜索，14 个达到 1000 万结点上限；K≤10 的案例全部完成搜索。",
    "贪心策略 1 已经是很强的基线。精确组总目标值只下降 0.711%，改进案例平均改进 4.80%，单案例最大改进 32.23%；回溯法的主要价值是量化差距和发现局部更优分配，而不是全面替代贪心。",
    "搜索规模随 K 快速增长。K=13-15 仍有 80% 的案例完成搜索，K=16-80 降至 5%，K=81-499 为 0；在 500 万结点上限下，K≈15 是从“多数可证明最优”走向“几乎只能得到可行解”的分界区间。",
    "anytime 机制是大规模场景的必要设计。全量 10000 个案例在 20 万结点上限下全部返回可行解，2288 个证明最优，3713 个改进贪心；未完成搜索不等于失败，而是明确标注为“未证明最优”。",
    "下界和对称性是决定搜索效率的关键。当前后缀下界忽略了时间冲突和机位占用，导致大规模案例中剪枝偏弱；强下界、等价机位合并、问题分解和束搜索是后续最值得尝试的改进方向。",
    "实验方法上，固定随机种子、统一二进制格式、逐案例 CSV、独立校验和分组统计保证了结果可复现；同时报告目标值、结点数、耗时、完成状态和最大/均值，避免只用总目标值掩盖局部异常。",
]:
    bullet(text)
body("从算法选择的角度看，停机位调度问题不存在“一种算法通吃所有规模”的方案。小规模可以用回溯/分支限界证明最优；中等规模可以用束搜索、限制差异搜索或分解算法；大规模更适合贪心、局部搜索和大邻域搜索。实际系统还应考虑飞机延误、机位临时关闭、旅客转机等动态因素，这些会进一步削弱离线精确搜索的价值。")
body("本实验的工程代码已经为后续实验提供了统一的数据结构、校验函数、基准程序和结果格式。实验三可以在当前回溯框架上加入更强的下界和分支限界；实验四可以把束搜索、局部搜索或遗传算法作为大规模启发式，与本次的精确结果进行对比。")

# ------------------------------------------------------------------ 七、问题
heading("七、实验中出现的问题及总结", 1)
body("实验过程中遇到并解决了以下问题。")
body("（1）初始上界与可行性的关系。回溯法如果在搜索前没有可行解，一旦触发结点上限就可能返回不可行解。现在的实现对贪心初始解先做 validateSolution，只有合法时才作为 bestAssign；搜索只接受严格更优的完整解。这样无论是否触发上限，返回解都可行。")
body("（2）complete 语义容易混淆。早期版本只用一个 feasible 标志，无法区分“搜索完整、证明最优”和“触发上限、只得到可行解”。现在 Solution 增加 complete、timeLimitReached、nodeLimitReached，基准程序据此输出 optimal/node_limit/time_limit；报告中也明确说明 complete=false 的结果不能声称最优。")
body("（3）基准程序的状态统计曾经把不可行解计入最优。最初只根据 complete 分支统计，未先判断 feasible；现已改为先判断 !feasible，再判断 complete，最后才计入受限，避免把异常结果误报为 optimal。")
body("（4）按 K 抽样需要跳过连续案例。数据按参数组合连续存放，直接用 --start/--count 只能取到一段连续的 K，无法构造 K=13..499 的分层样本。为此给 backtrack_benchmark 增加 --min-k、--max-k 和 --stride 选项，并在启动时校验参数范围；可扩展性组就是用多段命令拼接得到的。")
body("（5）结点上限先于时间上限触发。实验中所有受限案例都是 node_limit，time_limit 为 0。原因是每 1024 个结点才检查一次时钟，而 500 万或 1000 万结点在数百毫秒内就能耗尽；这说明在当前规模下，结点数是更直接的预算控制量。")
body("（6）计时包含预处理和贪心初始解。timeMs 从 BacktrackingSearch 构造开始，包含排序、下界计算、贪心初始解和搜索本身，因此小规模案例的平均耗时只有几微秒到几毫秒，不能完全归因于 DFS。报告在比较算法时主要看趋势和结点数，不把绝对耗时当作唯一指标。")
body("（7）完整数据集体积较大。10000 个案例约 59 MB，不适合全部放入提交压缩包。工程保留 combos.csv、生成器、12 个代表性样例和完整结果 CSV；执行 generate_cases 可以重建全部案例。")
body("（8）可扩展性实验的命令较多。K=13、14、15 需要用不同的起始编号分别运行，K=16..80 和 K=81..499 需要用 --stride 抽样；这些命令已整理到附录 A，结果 CSV 也随工程提交，便于复核。")
body("总结来说，本次实验的主要收获不是把回溯法调到多快，而是建立了一个可验证的精确/近似框架：用贪心给出可行上界，用下界和排序控制搜索，用 anytime 机制处理大规模，用 complete 标志诚实地区分最优与可行。这个框架可以直接扩展到实验三的分支限界和实验四的启发式方法。")

# ------------------------------------------------------------------ 参考文献
heading("参考文献", 1)
for text in [
    "[1] 算法分析与设计课程组. 算法分析与设计综合实验：停机位调度问题[Z]. 2026.",
    "[2] Cormen T H, Leiserson C E, Rivest R L, Stein C. Introduction to Algorithms[M]. 4th ed. Cambridge, MA: MIT Press, 2022.",
    "[3] Pinedo M L. Scheduling: Theory, Algorithms, and Systems[M]. 5th ed. Cham: Springer, 2016.",
    "[4] Wolsey L A. Integer Programming[M]. 2nd ed. Hoboken, NJ: Wiley, 2020.",
]:
    p = doc.add_paragraph(style="Normal")
    p.paragraph_format.first_line_indent = None
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run(text)
    set_run_font(run, size=10.5)

# ------------------------------------------------------------------ 附录
heading("附录 A  工程结构与运行方式", 1)
body("提交工程按数据结构、案例读写、算法实现、命令行工具和结果文档五部分组织。核心文件如表 13 所示。")
caption("工程核心文件")
table(
    ["文件/目录", "作用"],
    [
        ["CMakeLists.txt", "构建 airport_core、命令行工具和 CTest"],
        ["include/case.h", "Case、Stand、Plane 数据结构"],
        ["include/io.h、src/io.cpp", "二进制案例读写、validateCase、saveCase/loadCase"],
        ["include/solver.h", "Solution、Solver、GreedySolver、BacktrackingSolver 接口"],
        ["src/greedy.cpp", "两种贪心策略"],
        ["src/backtracking.cpp", "回溯法：排序、后缀下界、DFS、时间/结点上限"],
        ["src/utils.cpp", "calculateObjective、validateSolution、isStandAvailable"],
        ["tools/generate_cases.cpp", "生成 combos.csv 和 10000 个案例"],
        ["tools/validate_all.cpp", "批量校验案例和贪心解"],
        ["tools/benchmark.cpp", "10000 案例贪心对比"],
        ["tools/backtracking_benchmark.cpp", "回溯/贪心逐案例对比，支持 K 区间和 stride"],
        ["tools/solve_case.cpp", "打印单案例的贪心/回溯分配过程"],
        ["data/combos.csv、data/sample_cases", "参数组合和 12 个代表性样例"],
        ["results/", "CSV、统计 JSON、校验摘要"],
        ["docs/", "实验一/二报告和图表"],
    ],
    [2.2, 4.0], font_size=8.6, left_first=True,
    align={1: WD_ALIGN_PARAGRAPH.LEFT},
)
body("构建和运行方式如下（以 build 目录为例；作者实测使用 out/Release，命令中的路径相应替换）：")
code_block("Build and run", [
    "cmake -S . -B build -DCMAKE_BUILD_TYPE=Release",
    "cmake --build build -j",
    "",
    "# 生成完整数据（约 59 MB）",
    "./build/bin/generate_cases --out-dir data",
    "",
    "# 精确/近精确组",
    "./build/bin/backtrack_benchmark --start 0 --count 3000 \\",
    "    --min-k 0 --max-k 11 --time-limit-ms 2000 --node-limit 10000000 \\",
    "    --data-dir data/cases --out results/backtracking_benchmark.csv",
    "",
    "# 全量压力测试",
    "./build/bin/backtrack_benchmark --start 0 --count 10000 \\",
    "    --min-k 0 --max-k 1000 --time-limit-ms 200 --node-limit 200000 \\",
    "    --data-dir data/cases --out results/backtracking_stress_all.csv",
    "",
    "ctest --test-dir build --output-on-failure",
])
body("可扩展性抽样由以下五段命令组成，分别输出到临时 CSV，再按 CaseId 合并为 results/backtracking_scalability.csv；合并只做行拼接，不改变任何目标值或统计口径。")
code_block("Scalability sampling", [
    "# K=13, 14, 15 各 10 个",
    "./build/bin/backtrack_benchmark --start 1300 --count 10 --min-k 13 --max-k 13 \\",
    "    --time-limit-ms 1000 --node-limit 5000000 --data-dir data/cases --out /tmp/bt13.csv",
    "./build/bin/backtrack_benchmark --start 1400 --count 10 --min-k 14 --max-k 14 \\",
    "    --time-limit-ms 1000 --node-limit 5000000 --data-dir data/cases --out /tmp/bt14.csv",
    "./build/bin/backtrack_benchmark --start 500 --count 10 --min-k 15 --max-k 15 \\",
    "    --time-limit-ms 1000 --node-limit 5000000 --data-dir data/cases --out /tmp/bt15.csv",
    "",
    "# K=16..80，每 100 个取 1 个，共 40 个",
    "./build/bin/backtrack_benchmark --start 3000 --count 4000 --stride 100 \\",
    "    --min-k 16 --max-k 80 --time-limit-ms 1000 --node-limit 5000000 \\",
    "    --data-dir data/cases --out /tmp/bt_mid.csv",
    "",
    "# K=81..499，每 100 个取 1 个，共 30 个",
    "./build/bin/backtrack_benchmark --start 7000 --count 3000 --stride 100 \\",
    "    --min-k 81 --max-k 1000 --time-limit-ms 1000 --node-limit 5000000 \\",
    "    --data-dir data/cases --out /tmp/bt_large.csv",
])
body("提交目录中的 data/sample_cases 保留 12 个代表性案例，覆盖 K=6、7、9、10、13、22、49、258、319、340、377、499；data/combos.csv 给出全部 100 种参数组合；完整案例可由 generate_cases 重建。若只使用样例目录，CTest 会自动切换到 validate_sample、benchmark_sample 和 backtracking_sample 三个测试。")
body("报告中的统计由 results/backtracking_stats.json 汇总，图表由 docs/make_exp2_figures.py 生成；原始逐案例数据保存在 results/backtracking_benchmark.csv、backtracking_scalability.csv 和 backtracking_stress_all.csv 中，任何数字都可以从这三个文件重新计算。")

doc.save(OUT)
print("saved", OUT, OUT.stat().st_size)
