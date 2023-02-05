import pyecharts.options as opts

ANIMATION_OFF = opts.AnimationOpts(
    animation=False,
)

TOOLBOX_ONLY_SAVE_PNG_WHITE_2X = opts.ToolboxOpts(
    pos_left="5px",
    pos_top="5px",
    feature=opts.ToolBoxFeatureOpts(
        save_as_image=opts.ToolBoxFeatureSaveAsImageOpts(
            type_="png",
            title="下载",
            background_color="#FFFFFF",
            pixel_ratio=2,
        ),
        restore=None,  # type: ignore
        data_view=None,  # type: ignore
        data_zoom=None,  # type: ignore
        magic_type=None,  # type: ignore
        brush=None,  # type: ignore
    ),
)

CALENDAR_MONTH_CHINESE_DAY_YEAR_HIDE = {
    "daylabel_opts": opts.CalendarDayLabelOpts(
        is_show=False,
    ),
    "monthlabel_opts": opts.CalendarMonthLabelOpts(
        name_map="cn",
    ),
    "yearlabel_opts": opts.CalendarYearLabelOpts(
        is_show=False,
    ),
}

VISUALMAP_JIANSHU_COLOR = ("#fbe2de", "#f7c5bd", "#f2a99c", "#ee8c7b", "#ea6f5a")

JIANSHU_COLOR = "#ea6f5a"

NO_LEGEND = opts.LegendOpts(
    is_show=False,
)
