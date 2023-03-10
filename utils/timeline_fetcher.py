from datetime import datetime
from re import findall
from typing import Dict, List

from JianshuResearchTools.assert_funcs import AssertType
from JianshuResearchTools.basic_apis import GetUserTimelineHtmlDataApi
from JianshuResearchTools.convert import (
    CollectionSlugToCollectionUrl,
    UserSlugToUserUrl,
    UserUrlToUserSlug,
)


def article_slug_to_article_url(article_slug: str) -> str:
    AssertType(article_slug, str)
    return f"https://www.jianshu.com/p/{article_slug}"


def notebook_slug_to_notebook_url(notebook_slug: str) -> str:
    AssertType(notebook_slug, str)
    return f"https://www.jianshu.com/nb/{notebook_slug}"


def get_user_timeline_info(user_url: str, max_id: int = 1000000000) -> List[Dict]:
    """获取用户动态信息

    ! 这是对 JRT 中关注文集数据解析错误的修正，仅作为临时解决方案使用
    ！在极少数情况下可能会遇到不在可解析列表中的动态类型，此时程序会跳过这条动态，不会抛出异常

    Args:
        user_url (str): 用户个人主页 URL
        max_id (int, optional): 最大 id，值等于上一次获取到的数据中最后一项的 operation_id. Defaults to 1000000000.

    Returns:
        List[Dict]: 用户动态信息
    """
    user_slug = UserUrlToUserSlug(user_url)
    html_obj = GetUserTimelineHtmlDataApi(user_slug, max_id)
    blocks = [x.__copy__() for x in html_obj.xpath("//li[starts-with(@id, 'feed-')]")]
    result = []

    for block in blocks:
        item_data = {
            "operation_id": int(block.xpath("//li/@id")[0][5:]),
            "operation_type": block.xpath(
                "//span[starts-with(@data-datetime, '20')]/@data-type"
            )[0],
            "operation_time": datetime.fromisoformat(
                block.xpath("//span[starts-with(@data-datetime, '20')]/@data-datetime")[
                    0
                ]
            ),
        }

        if item_data["operation_type"] == "like_note":  # 对文章点赞
            item_data["operation_type"] = "like_article"  # 鬼知道谁把对文章点赞写成 like_note 的
            item_data["target_article_title"] = block.xpath(
                "//a[@class='title']/text()"
            )[0]
            item_data["target_article_url"] = article_slug_to_article_url(
                block.xpath("//a[@class='title']/@href")[0][3:]
            )
            item_data["target_user_name"] = block.xpath(
                "//div[@class='origin-author']/a/text()"
            )[0]
            item_data["target_user_url"] = UserSlugToUserUrl(
                block.xpath("//div[@class='origin-author']/a/@href")[0].split("/")[-1]
            )
            item_data["target_article_reads_count"] = int(
                block.xpath("//div[@class='meta']/a/text()")[1]
            )
            item_data["target_article_likes_count"] = int(
                block.xpath("//div[@class='meta']/span/text()")[0]
            )
            try:
                item_data["target_article_comments_count"] = int(
                    block.xpath("//div[@class='meta']/a/text()")[3]
                )
            except IndexError:  # 文章没有评论或评论区关闭
                item_data["target_article_comments_count"] = 0
            try:
                item_data["target_article_description"] = block.xpath(
                    "//p[@class='abstract']/text()"
                )[0]
            except IndexError:  # 文章没有摘要
                item_data["target_article_description"] = ""

        elif item_data["operation_type"] == "like_comment":  # 对评论点赞
            item_data["comment_content"] = "\n".join(
                block.xpath("//p[@class='comment']/text()")
            )
            item_data["target_article_title"] = block.xpath(
                "//blockquote/div/span/a/text()"
            )[0]
            item_data["target_article_url"] = article_slug_to_article_url(
                block.xpath("//blockquote/div/span/a/@href")[0][3:]
            )
            item_data["target_user_name"] = block.xpath("//blockquote/div/a/text()")[0]
            item_data["target_user_url"] = UserSlugToUserUrl(
                block.xpath("//blockquote/div/a/@href")[0][3:]
            )

        elif item_data["operation_type"] == "share_note":  # 发表文章
            item_data["operation_type"] = "publish_article"  # 鬼知道谁把发表文章写成 share_note 的
            item_data["target_article_title"] = block.xpath(
                "//a[@class='title']/text()"
            )[0]
            item_data["target_article_url"] = article_slug_to_article_url(
                block.xpath("//a[@class='title']/@href")[0][3:]
            )
            item_data["target_article_reads_count"] = int(
                block.xpath("//div[@class='meta']/a/text()")[1]
            )
            item_data["target_article_likes_count"] = int(
                block.xpath("//div[@class='meta']/span/text()")[0]
            )
            item_data["target_article_description"] = "\n".join(
                block.xpath("//p[@class='abstract']/text()")
            )
            try:
                item_data["target_article_comments_count"] = int(
                    block.xpath("//div[@class='meta']/a/text()")[3]
                )
            except IndexError:
                item_data["target_article_comments_count"] = 0

        elif item_data["operation_type"] == "comment_note":  # 发表评论
            item_data[
                "operation_type"
            ] = "comment_article"  # 鬼知道谁把评论文章写成 comment_note 的
            item_data["comment_content"] = "\n".join(
                block.xpath("//p[@class='comment']/text()")
            )
            item_data["target_article_title"] = block.xpath(
                "//a[@class='title']/text()"
            )[0]
            item_data["target_article_url"] = article_slug_to_article_url(
                block.xpath("//a[@class='title']/@href")[0][3:]
            )
            item_data["target_user_name"] = block.xpath(
                "//div[@class='origin-author']/a/text()"
            )[0]
            item_data["target_user_url"] = UserSlugToUserUrl(
                block.xpath("//div[@class='origin-author']/a/@href")[0].split("/")[-1]
            )
            item_data["target_article_reads_count"] = int(
                block.xpath("//div[@class='meta']/a/text()")[1]
            )
            item_data["target_article_likes_count"] = int(
                block.xpath("//div[@class='meta']/span/text()")[0]
            )
            try:
                item_data["target_article_comments_count"] = int(
                    block.xpath("//div[@class='meta']/a/text()")[3]
                )
            except IndexError:  # 文章没有评论或评论区关闭
                item_data["target_article_comments_count"] = 0
            try:
                item_data["target_article_description"] = block.xpath(
                    "//p[@class='abstract']/text()"
                )[0]
            except IndexError:  # 文章没有描述
                item_data["target_article_description"] = ""
            try:
                item_data["target_article_rewards_count"] = int(
                    block.xpath("//div[@class='meta']/span/text()")[1]
                )
            except IndexError:  # 没有赞赏数据
                item_data["target_article_rewards_count"] = 0

        elif item_data["operation_type"] == "like_notebook":  # 关注文集
            item_data[
                "operation_type"
            ] = "follow_notebook"  # 鬼知道谁把关注文集写成 like_notebook 的
            item_data["target_notebook_title"] = block.xpath(
                "//a[@class='title']/text()"
            )[0]
            # 此处对 JRT 中的错误进行了修复
            item_data["target_notebook_url"] = notebook_slug_to_notebook_url(
                block.xpath("//a[@class='title']/@href")[0][4:]
            )
            item_data["target_notebook_avatar_url"] = block.xpath(
                "//div[@class='follow-detail']/div/a/img/@src"
            )[0]
            item_data["target_user_name"] = block.xpath("//a[@class='creater']/text()")[
                0
            ]
            item_data["target_user_url"] = UserSlugToUserUrl(
                block.xpath("//a[@class='creater']/@href")[0][3:]
            )
            item_data["target_notebook_articles_count"] = int(
                findall(r"\d+", block.xpath("//div[@class='info'][1]/p/text()")[1])[0]
            )
            item_data["target_notebook_subscribers_count"] = int(
                findall(r"\d+", block.xpath("//div[@class='info'][1]/p/text()")[1])[1]
            )

        elif item_data["operation_type"] == "like_collection":  # 关注专题
            item_data[
                "operation_type"
            ] = "follow_collection"  # 鬼知道谁把关注专题写成 like_collection 的
            item_data["target_collection_title"] = block.xpath(
                "//a[@class='title']/text()"
            )[0]
            item_data["target_collection_url"] = CollectionSlugToCollectionUrl(
                block.xpath("//a[@class='title']/@href")[0][3:]
            )
            item_data["target_collection_avatar_url"] = block.xpath(
                "//div[@class='follow-detail']/div/a/img/@src"
            )[0]
            item_data["target_user_name"] = block.xpath("//a[@class='creater']/text()")[
                0
            ]
            item_data["target_user_url"] = UserSlugToUserUrl(
                block.xpath("//a[@class='creater']/@href")[0][3:]
            )
            item_data["target_collection_articles_count"] = int(
                findall(r"\d+", block.xpath("//div[@class='info'][1]/p/text()")[1])[0]
            )
            item_data["target_collection_subscribers_count"] = int(
                findall(r"\d+", block.xpath("//div[@class='info'][1]/p/text()")[1])[1]
            )

        elif item_data["operation_type"] == "like_user":  # 关注用户
            item_data["operation_type"] = "follow_user"  # 鬼知道谁把关注用户写成 like_user 的
            item_data["target_user_name"] = block.xpath(
                "//div[@class='info']/a[@class='title']/text()"
            )[0]
            item_data["target_user_url"] = UserSlugToUserUrl(
                block.xpath("//div[@class='info']/a[@class='title']/@href")[0][3:]
            )
            item_data["target_user_wordage"] = int(
                findall(
                    r"\d+",
                    block.xpath(
                        "//div[@class='follow-detail']/div[@class='info']/p/text()"
                    )[0],
                )[0]
            )
            item_data["target_user_fans_count"] = int(
                findall(
                    r"\d+",
                    block.xpath(
                        "//div[@class='follow-detail']/div[@class='info']/p/text()"
                    )[0],
                )[1]
            )
            item_data["target_user_likes_count"] = int(
                findall(
                    r"\d+",
                    block.xpath(
                        "//div[@class='follow-detail']/div[@class='info']/p/text()"
                    )[0],
                )[2]
            )
            item_data["target_user_description"] = "\n".join(
                block.xpath("//div[@class='signature']/text()")
            )

        result.append(item_data)
    return result
