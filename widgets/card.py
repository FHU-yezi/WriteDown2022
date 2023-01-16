from pywebio.output import Output, put_widget


def put_app_card(
    name: str, url: str, desc: str
) -> Output:
    tpl: str = """
    <div class="card" style="padding: 20px; padding-bottom: 10px; margin-bottom: 20px; border-radius: 20px;">
        <b style="font-size: 20px; padding-bottom: 15px;">{{name}}</b>
        <p>{{desc}}</p>
        <button class="btn btn-outline-secondary" style="position: absolute; top: 16px; right: 30px;" onclick="window.open('{{url}}', '_blank')"><b>&gt;</b></button>
    </div>
    """
    return put_widget(
        tpl,
        {
            "name": name,
            "desc": desc,
            "url": url,
        },
    )
