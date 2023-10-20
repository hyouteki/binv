from imgui_bundle import immapp, hello_imgui, imgui, imgui_md, implot, ImVec2
from imgui_bundle import im_file_dialog as ifd
import numpy as np

ALL_THEMES = [
    hello_imgui.ImGuiTheme_.darcula_darker,
    hello_imgui.ImGuiTheme_.darcula,
    hello_imgui.ImGuiTheme_.imgui_colors_classic,
    hello_imgui.ImGuiTheme_.imgui_colors_dark,
    hello_imgui.ImGuiTheme_.imgui_colors_light,
    hello_imgui.ImGuiTheme_.material_flat,
    hello_imgui.ImGuiTheme_.photoshop_style,
    hello_imgui.ImGuiTheme_.gray_variations,
    hello_imgui.ImGuiTheme_.gray_variations_darker,
    hello_imgui.ImGuiTheme_.microsoft_style,
    hello_imgui.ImGuiTheme_.cherry,
    hello_imgui.ImGuiTheme_.light_rounded,
    hello_imgui.ImGuiTheme_.so_dark_accent_blue,
    hello_imgui.ImGuiTheme_.so_dark_accent_yellow,
    hello_imgui.ImGuiTheme_.so_dark_accent_red,
    hello_imgui.ImGuiTheme_.black_is_black,
    hello_imgui.ImGuiTheme_.white_is_white,
]

ALL_THEMES_NAMES = [theme.name for theme in ALL_THEMES]

CONTEXT = [False, None, None]
THEMES_WINDOW_VISIBILITY_INDEX = 0
SELECTED_OPEN_FILE_PATH_INDEX = 1
SELECTED_SAVE_FILE_PATH_INDEX = 2


def openFileDialog():
    if imgui.button("Open file"):
        ifd.FileDialog.instance().open(
            "OpenFileDialog",
            "Open file",
            "*.*",
            True,
        )
    if ifd.FileDialog.instance().is_done("OpenFileDialog"):
        if ifd.FileDialog.instance().has_result():
            res = ifd.FileDialog.instance().get_results()
            filenames = [f.path() for f in res]
            CONTEXT[SELECTED_OPEN_FILE_PATH_INDEX] = "\n  ".join(filenames)
        ifd.FileDialog.instance().close()
        getFileByteFrequency()


def saveFileDialog():
    if imgui.button("Save file"):
        ifd.FileDialog.instance().save(
            "SaveFileDialog", "Save visualization as image", "*.png .png"
        )
    if ifd.FileDialog.instance().is_done("SaveFileDialog"):
        if ifd.FileDialog.instance().has_result():
            CONTEXT[SELECTED_SAVE_FILE_PATH_INDEX] = (
                ifd.FileDialog.instance().get_result().path()
            )
        ifd.FileDialog.instance().close()


@immapp.static(currentThemeIndex=0)
def themePicker():
    if imgui.button("Themes"):
        CONTEXT[THEMES_WINDOW_VISIBILITY_INDEX] = not CONTEXT[
            THEMES_WINDOW_VISIBILITY_INDEX
        ]
    if CONTEXT[THEMES_WINDOW_VISIBILITY_INDEX]:
        imgui.begin(
            "Themes",
            flags=imgui.WindowFlags_.always_auto_resize
            | imgui.WindowFlags_.no_collapse,
        )
        static = themePicker
        changed, static.currentThemeIndex = imgui.list_box(
            "##Theme",
            static.currentThemeIndex,
            ALL_THEMES_NAMES,
            len(ALL_THEMES_NAMES),
        )
        if changed:
            hello_imgui.apply_theme(ALL_THEMES[static.currentThemeIndex])
            CONTEXT[THEMES_WINDOW_VISIBILITY_INDEX] = False
        imgui.end()


freq = []
scale_min = 0
scale_max = 6.3
freq_max = 6.3
colormap = implot.Colormap_.viridis.value


hm_flags = implot.HeatmapFlags_.none
axes_flags = (
    implot.AxisFlags_.no_label
    | implot.AxisFlags_.no_highlight
    | implot.AxisFlags_.no_tick_labels
    | implot.AxisFlags_.no_tick_marks
)


def getFileByteFrequency():
    global freq, scale_max, freq_max
    if CONTEXT[SELECTED_OPEN_FILE_PATH_INDEX] is None:
        return
    freq = [[0 for _ in range(256)] for _ in range(256)]
    scale_max = 1
    with open(CONTEXT[SELECTED_OPEN_FILE_PATH_INDEX], "rb") as file:
        byte = file.read(1)
        pre = int.from_bytes(byte, byteorder="little")
        while byte:
            x = pre
            byte = file.read(1)
            pre = int.from_bytes(byte, byteorder="little")
            y = pre
            freq[x][y] += 1
            scale_max = max(scale_max, freq[x][y])
    freq_max = scale_max


def heatmap():
    if CONTEXT[SELECTED_OPEN_FILE_PATH_INDEX] is None:
        return
    imgui.set_next_item_width(225)
    if imgui.input_text(
        label="##Selected file name for visualization",
        str=CONTEXT[SELECTED_OPEN_FILE_PATH_INDEX].split("\\")[-1],
        flags=imgui.InputTextFlags_.read_only,
    ):
        pass
    imgui.same_line()
    global colormap, scale_min, scale_max, hm_flags
    if implot.colormap_button(
        implot.get_colormap_name(colormap), ImVec2(225, 0), colormap
    ):
        colormap = (colormap + 1) % implot.get_colormap_count()
        implot.bust_color_cache("##Heatmap1")
        implot.bust_color_cache("##Heatmap2")
    imgui.same_line()
    imgui.set_next_item_width(225)
    out = imgui.slider_float2("## Min / Max bs", [scale_min, scale_max], 0, freq_max)
    if out[0]:
        scale_min = out[1][0]
        scale_max = out[1][1]
    imgui.same_line()
    out = imgui.checkbox_flags("Column Major", hm_flags, implot.HeatmapFlags_.col_major)
    if out[0]:
        hm_flags = out[1]
    implot.push_colormap(colormap)
    if implot.begin_plot("##Heatmap1", ImVec2(-1, -1), flags=implot.Flags_.no_legend):
        implot.setup_axes(None, None, axes_flags, axes_flags)
        implot.plot_heatmap(
            label_id="heat",
            values=np.array(freq),
            scale_min=scale_min,
            scale_max=scale_max,
            label_fmt="",
            flags=hm_flags,
        )
        implot.end_plot()
    imgui.same_line()
    implot.pop_colormap()


def main():
    imgui.dummy((0, 3))
    imgui.indent(7)

    openFileDialog()
    imgui.same_line()
    themePicker()
    # imgui.same_line()
    # saveFileDialog()

    heatmap()


if __name__ == "__main__":
    immapp.run(
        gui_function=main,
        with_implot=True,
        window_title="Dynamic Binary Visualizer",
        window_size=(1000, 800),
        with_markdown=True,
    )
