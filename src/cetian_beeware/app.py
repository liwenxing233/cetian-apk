# src/cetian_beeware/app.py
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from datetime import date, datetime
from lunar_python import Solar

from .constants import HOUR_RANGES, ZHI
from .calendar_utils import solar_to_lunar, get_bazi
from .core.chart import build_chart


class CeTianApp(toga.App):
    def startup(self):
        self.main_window = toga.MainWindow(title=self.formal_name)

        # 主容器
        self.main_box = toga.Box(style=Pack(direction=COLUMN, padding=5, background_color="#F4F1EB"))

        # ================= 1. 输入区域 (恢复年月日标签) =================
        input_box = toga.Box(style=Pack(direction=COLUMN, padding=5, margin_bottom=5, background_color="#FFFFFF"))

        row1 = toga.Box(style=Pack(direction=ROW, alignment=CENTER, margin_bottom=5))
        self.year_input = toga.TextInput(value="1990", style=Pack(flex=2, margin_right=2))
        row1.add(self.year_input)
        row1.add(toga.Label("年", style=Pack(margin_right=5)))

        self.month_input = toga.TextInput(value="1", style=Pack(flex=1, margin_right=2))
        row1.add(self.month_input)
        row1.add(toga.Label("月", style=Pack(margin_right=5)))

        self.day_input = toga.TextInput(value="1", style=Pack(flex=1, margin_right=2))
        row1.add(self.day_input)
        row1.add(toga.Label("日", style=Pack(margin_right=10)))

        self.gender_select = toga.Selection(items=["男", "女"], style=Pack(width=60))
        row1.add(self.gender_select)

        row2 = toga.Box(style=Pack(direction=ROW, alignment=CENTER))
        self.hour_select = toga.Selection(items=list(HOUR_RANGES.keys()), style=Pack(flex=2, margin_right=5))
        row2.add(self.hour_select)

        row2.add(toga.Label("流年", style=Pack(margin_right=5)))
        self.liunian_input = toga.TextInput(value=str(datetime.now().year), style=Pack(width=50, margin_right=5))
        row2.add(self.liunian_input)

        self.btn = toga.Button("排盘", on_press=self.paipan_clicked,
                               style=Pack(background_color="#C6A26E", color="#FFFFFF", width=60))
        row2.add(self.btn)

        input_box.add(row1)
        input_box.add(row2)
        self.main_box.add(input_box)

        # ================= 2. 结果显示区域 =================
        self.result_box = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER))
        self.scroll_container = toga.ScrollContainer(content=self.result_box, style=Pack(flex=1))
        self.main_box.add(self.scroll_container)

        self.main_window.content = self.main_box
        self.main_window.show()

    def paipan_clicked(self, widget):
        try:
            y = int(self.year_input.value)
            m = int(self.month_input.value)
            d = int(self.day_input.value)
            solar_date = date(y, m, d)

            hour_zhi = HOUR_RANGES.get(self.hour_select.value, "子")
            gender = self.gender_select.value

            ln_year = int(self.liunian_input.value)
            ln_solar = Solar.fromYmdHms(ln_year, 6, 1, 12, 0, 0)
            ln_lunar = ln_solar.getLunar()

            lunar = solar_to_lunar(solar_date, hour_zhi)
            bazi = get_bazi(solar_date, hour_zhi)

            data = build_chart(
                lunar["year_zhi"], bazi["年干"], lunar["month"], lunar["day"],
                hour_zhi, gender,
                liunian_zhi=ln_lunar.getYearZhi(), liunian_gan=ln_lunar.getYearGan()
            )

            self.render_chart(data, bazi, ln_year)

        except Exception as e:
            self.main_window.info_dialog("排盘错误", f"请检查输入格式！\n{str(e)}")

    def make_palace_cell(self, zhi, info, ming_gong, shen_gong, liunian, da_xian_map):
        # 给每个格子内部包裹一层，防止内容撑开外部框架
        cell = toga.Box(style=Pack(direction=COLUMN, background_color="#FFFFFF", padding=3, margin=1))

        # 头部 (宫名 + 地支)
        badges = []
        if zhi == ming_gong: badges.append("命")
        if zhi == shen_gong: badges.append("身")
        if liunian and zhi == liunian["liu_ming"]: badges.append("流")
        badge_str = f"[{'/'.join(badges)}]" if badges else ""

        header = toga.Box(style=Pack(direction=ROW))
        header.add(toga.Label(f"{info['shi_xiang']}", style=Pack(font_size=10, font_weight="bold")))
        if badge_str:
            header.add(toga.Label(badge_str, style=Pack(font_size=8, color="#D32F2F", margin_left=2)))
        header.add(toga.Label(zhi, style=Pack(font_size=8, color="#7A7A7A", flex=1, text_align="right")))
        cell.add(header)

        # 主星
        zheng_list = info["zheng_yao"]
        if zheng_list:
            name = zheng_list[0]['name']
            mw = zheng_list[0].get('mw', '')
            zheng_str = f"{name} {mw}".strip()
            zheng_color = "#D32F2F" if mw == "庙" else (
                "#F57C00" if mw == "旺" else ("#388E3C" if mw == "乐" else "#8E5425"))
        else:
            zheng_str = "—"
            zheng_color = "#7A7A7A"
        cell.add(toga.Label(zheng_str, style=Pack(font_size=13, font_weight="bold", color=zheng_color, margin_top=1,
                                                  margin_bottom=1)))

        # 长生
        cell.add(toga.Label(info["chang_sheng"], style=Pack(font_size=8, color="#1565C0")))

        # 附星 (最多只显示 3 个，绝对防撑爆)
        all_fu = [s['name'] for s in info["fu_jia"] + info["extra"]]
        if all_fu:
            cell.add(toga.Label(" ".join(all_fu[:3]), style=Pack(font_size=8, color="#7A7A7A")))

        # 地星 (只取第一个)
        dx_names = [s["name"] for s in info["di_xing"]]
        if dx_names:
            cell.add(toga.Label("地:" + dx_names[0], style=Pack(font_size=8, color="#D84315")))

        # 限与流年 (拆分成两行极短的字，彻底杜绝挤爆列宽)
        dx_text = " ".join(da_xian_map.get(zhi, []))
        ln_text = ""
        if liunian:
            ln_parts = []
            ln_parts.extend(liunian["stars"].get(zhi, [])[:1])  # 流年星只取1个
            if zhi in liunian["shen_sha"]: ln_parts.append(liunian["shen_sha"][zhi])
            ln_text = " ".join(ln_parts)

        if dx_text:
            cell.add(toga.Label(f"限: {dx_text}", style=Pack(font_size=7, color="#7A7A7A")))
        if ln_text:
            cell.add(toga.Label(f"流: {ln_text[:6]}", style=Pack(font_size=7, color="#D32F2F", font_weight="bold")))

        return cell

    def render_chart(self, data, bazi, ln_year):
        self.result_box.clear()

        chart = data["chart"]
        ming_gong = data["ming_gong"]
        shen_gong = data["shen_gong"]
        liunian = data.get("liunian")
        ge_ju = data.get("ge_ju", [])

        da_xian_map = {}
        for start, end, pos in data["da_xian"]:
            da_xian_map.setdefault(pos, []).append(f"{start}~{end}")

        # 使用 flex=1 让它完全自适应手机屏幕
        grid_box = toga.Box(style=Pack(direction=ROW, flex=1, background_color="#E0E0E0"))

        # 左侧列 (巳辰卯寅)
        left_col = toga.Box(style=Pack(direction=COLUMN, flex=1))
        for z in ["巳", "辰", "卯", "寅"]:
            cell = self.make_palace_cell(z, chart[z], ming_gong, shen_gong, liunian, da_xian_map)
            cell.style.update(flex=1)
            left_col.add(cell)
        grid_box.add(left_col)

        # 中间列 (午未，中宫，丑子)
        mid_col = toga.Box(style=Pack(direction=COLUMN, flex=2))

        top_row = toga.Box(style=Pack(direction=ROW, flex=1))
        for z in ["午", "未"]:
            cell = self.make_palace_cell(z, chart[z], ming_gong, shen_gong, liunian, da_xian_map)
            cell.style.update(flex=1)
            top_row.add(cell)
        mid_col.add(top_row)

        # 中宫
        center_box = toga.Box(style=Pack(direction=COLUMN, flex=2, background_color="#F4F1EB", padding=5, margin=1))
        c_inner = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER))
        c_inner.add(toga.Label("策 天 飞 星", style=Pack(font_size=16, font_weight="bold", color="#C6A26E")))
        c_inner.add(toga.Label(f"{bazi['农历']}", style=Pack(font_size=10, font_weight="bold", margin_top=5)))
        c_inner.add(
            toga.Label(f"命:{ming_gong} 身:{shen_gong}", style=Pack(font_size=10, color="#8E5425", margin_top=5)))
        if liunian:
            c_inner.add(toga.Label(f"{ln_year}流年:{liunian['liu_ming']}",
                                   style=Pack(font_size=10, color="#D32F2F", margin_top=5)))
        if ge_ju:
            c_inner.add(toga.Label(f"【{','.join(ge_ju)}】",
                                   style=Pack(font_size=10, font_weight="bold", color="#E65100", margin_top=5)))
        center_box.add(c_inner)
        mid_col.add(center_box)

        bot_row = toga.Box(style=Pack(direction=ROW, flex=1))
        for z in ["丑", "子"]:
            cell = self.make_palace_cell(z, chart[z], ming_gong, shen_gong, liunian, da_xian_map)
            cell.style.update(flex=1)
            bot_row.add(cell)
        mid_col.add(bot_row)
        grid_box.add(mid_col)

        # 右侧列 (申酉戌亥)
        right_col = toga.Box(style=Pack(direction=COLUMN, flex=1))
        for z in ["申", "酉", "戌", "亥"]:
            cell = self.make_palace_cell(z, chart[z], ming_gong, shen_gong, liunian, da_xian_map)
            cell.style.update(flex=1)
            right_col.add(cell)
        grid_box.add(right_col)

        self.result_box.add(grid_box)


def main():
    return CeTianApp("策天十八飞星", "com.cetian.beeware")