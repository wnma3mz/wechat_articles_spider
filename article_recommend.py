# coding: utf-8
"""
微信推荐文章
"""
import argparse
import json
import pickle
from collections import Counter

import requests

parser = argparse.ArgumentParser(description="wechat article recommend analysis")
parser.add_argument("--url", type=str, help="wechat article url")
parser.add_argument("--nickname", type=str, help="wechat officename")
parser.add_argument(
    "--max_recursive", type=int, default=10, help="recommend url recursive depth"
)
parser.add_argument(
    "--high_frequency_value", type=int, default=20, help="max officename frequency"
)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"
}
relatedarticle_url = "https://mp.weixin.qq.com/mp/relatedarticle"


def write_data(res_lst, output_fname="graph.html"):
    # 绘制graph.html
    head = """
    <!DOCTYPE html>
    <meta charset="utf-8">
    <style>
        .link {
            fill: none;
            stroke: #666;
            stroke-width: 1.5px;
        }

        #licensing {
            fill: green;
        }

        .link.licensing {
            stroke: green;
        }

        .link.resolved {
            stroke-dasharray: 0, 2 1;
        }

        circle {
            fill: #ccc;
            stroke: #333;
            stroke-width: 1.5px;
        }

        text {
            font: 12px Microsoft YaHei;
            pointer-events: none;
            text-shadow: 0 1px 0 #fff, 1px 0 0 #fff, 0 -1px 0 #fff, -1px 0 0 #fff;
        }

        .linetext {
            font-size: 12px Microsoft YaHei;
        }
    </style>

    <body>
        <script src="https://d3js.org/d3.v3.min.js"></script>
        <script>
        var links = [
    """
    tail = """
    ]
       var nodes = {};

        links.forEach(function (link) {
            link.source = nodes[link.source] || (nodes[link.source] = { name: link.source });
            link.target = nodes[link.target] || (nodes[link.target] = { name: link.target });
        });

        var width = 1920, height = 1080;

        var force = d3.layout.force()
            .nodes(d3.values(nodes))
            .links(links)
            .size([width, height])
            .linkDistance(180)
            .charge(-1500)
            .on("tick", tick)
            .start();

        var svg = d3.select("body").append("svg")
            .attr("width", width)
            .attr("height", height);

        var marker =
            svg.append("marker")
                .attr("id", "resolved")
                .attr("markerUnits", "userSpaceOnUse")
                .attr("viewBox", "0 -5 10 10")
                .attr("refX", 32)
                .attr("refY", -1)
                .attr("markerWidth", 12)
                .attr("markerHeight", 12)
                .attr("orient", "auto")
                .attr("stroke-width", 2)
                .append("path")
                .attr("d", "M0,-5L10,0L0,5")
                .attr('fill', '#000000');

        var edges_line = svg.selectAll(".edgepath")
            .data(force.links())
            .enter()
            .append("path")
            .attr({
                'd': function (d) { return 'M ' + d.source.x + ' ' + d.source.y + ' L ' + d.target.x + ' ' + d.target.y },
                'class': 'edgepath',
                'id': function (d, i) { return 'edgepath' + i; }
            })
            .style("stroke", function (d) {
                var lineColor;
                lineColor = "#B43232";
                return lineColor;
            })
            .style("pointer-events", "none")
            .style("stroke-width", 0.5)
            .attr("marker-end", "url(#resolved)");

        var edges_text = svg.append("g").selectAll(".edgelabel")
            .data(force.links())
            .enter()
            .append("text")
            .style("pointer-events", "none")
            .attr({
                'class': 'edgelabel',
                'id': function (d, i) { return 'edgepath' + i; },
                'dx': 80,
                'dy': 0
            });

        edges_text.append('textPath')
            .attr('xlink:href', function (d, i) { return '#edgepath' + i })
            .style("pointer-events", "none")
            .text(function (d) { return d.rela; });

        var circle = svg.append("g").selectAll("circle")
            .data(force.nodes())
            .enter().append("circle")
            .style("fill", function (node) {
                var color;
                var link = links[node.index];
                color = "#F9EBF9";
                return color;
            })
            .style('stroke', function (node) {
                var color;
                var link = links[node.index];
                color = "#A254A2";
                return color;
            })
            .attr("r", 28)
            .on("click", function (node) {
                edges_line.style("stroke-width", function (line) {
                    console.log(line);
                    if (line.source.name == node.name || line.target.name == node.name) {
                        return 4;
                    } else {
                        return 0.5;
                    }
                });
            })
            .call(force.drag);

        var text = svg.append("g").selectAll("text")
            .data(force.nodes())
            .enter()
            .append("text")
            .attr("dy", ".35em")
            .attr("text-anchor", "middle")
            .style('fill', function (node) {
                var color;
                var link = links[node.index];
                color = "#A254A2";
                return color;
            }).attr('x', function (d) {
                var re_en = /[a-zA-Z]+/g;
                if (d.name.match(re_en)) {
                    d3.select(this).append('tspan')
                        .attr('x', 0)
                        .attr('y', 2)
                        .text(function () { return d.name; });
                }

                else if (d.name.length <= 4) {
                    d3.select(this).append('tspan')
                        .attr('x', 0)
                        .attr('y', 2)
                        .text(function () { return d.name; });
                } else {
                    var top = d.name.substring(0, 4);
                    var bot = d.name.substring(4, d.name.length);

                    d3.select(this).text(function () { return ''; });

                    d3.select(this).append('tspan')
                        .attr('x', 0)
                        .attr('y', -7)
                        .text(function () { return top; });

                    d3.select(this).append('tspan')
                        .attr('x', 0)
                        .attr('y', 10)
                        .text(function () { return bot; });
                }
            });

        function tick() {
            circle.attr("transform", transform1);
            text.attr("transform", transform2);

            edges_line.attr('d', function (d) {
                var path = 'M ' + d.source.x + ' ' + d.source.y + ' L ' + d.target.x + ' ' + d.target.y;
                return path;
            });

            edges_text.attr('transform', function (d, i) {
                if (d.target.x < d.source.x) {
                    bbox = this.getBBox();
                    rx = bbox.x + bbox.width / 2;
                    ry = bbox.y + bbox.height / 2;
                    return 'rotate(180 ' + rx + ' ' + ry + ')';
                }
                else {
                    return 'rotate(0)';
                }
            });
        }

        function linkArc(d) {
            return 'M ' + d.source.x + ' ' + d.source.y + ' L ' + d.target.x + ' ' + d.target.y
        }

        function transform1(d) {
            return "translate(" + d.x + "," + d.y + ")";
        }
        function transform2(d) {
            return "translate(" + (d.x) + "," + d.y + ")";
        }

    </script>
    """
    with open(output_fname, "w", encoding="utf-8") as f:
        f.write(head)
        for item in res_lst:
            if len(item["target"]) < 20:
                for target in item["target"]:
                    f.write(
                        '{ source: "'
                        + item["source"]
                        + '", target: "'
                        + target
                        + '" },'
                        + "\n"
                    )
        f.write(tail)


def merge_dict(source_set, lst):
    # 合并相同source的target
    res_lst = []
    for source in source_set:

        tmp = list(filter(lambda i: i["source"] == source, lst))
        tmp_set = set()
        for line in tmp:
            tmp_set = tmp_set | line["target"]
        res_lst.append({"source": source, "target": tmp_set})
    return res_lst


def get_recommend_article(article_url):
    params = {
        "action": "getlist",
        "count": 3,  # 可修改
        "begin": 0,
        "article_url": article_url,
    }
    res = requests.get(relatedarticle_url, headers=headers, params=params)
    return res.json()["list"]


def run(start_article_url, max_recursive=10, fname="d.pkl"):
    article_url_lst = [start_article_url]
    traverse_url_set = set()
    data_lst = []
    recursive_count = 0
    try:
        while recursive_count < max_recursive:
            tmp_url_set = set()
            # 遍历爬取的文章
            for article_url in article_url_lst:
                recommend_article_lst = get_recommend_article(article_url)
                data_lst.append({article_url: recommend_article_lst})  # 存储已经爬取的文章
                traverse_url_set.add(article_url)  # 已经爬取过
                # 获取新的推荐文章，避免重复用set
                for item in recommend_article_lst:
                    tmp_url_set.add(item["url"])
            # 如果已经爬取过，则跳过
            article_url_lst = []
            for article_url in tmp_url_set:
                if article_url not in traverse_url_set:
                    article_url_lst.append(article_url)
            print("第{}层: {}条数据".format(recursive_count, len(article_url_lst)))
            recursive_count += 1
    except Exception as e:
        print(e)
    finally:
        with open(fname, "wb") as f:
            pickle.dump(data_lst, f)


def analysis(url_nickname_dict, fname="d.pkl", high_frequency_value=20):
    """
    url_nickname_dict: 链接与公众号名字的k与v
    """
    with open(fname, "rb") as f:
        data_lst = pickle.load(f)

    # 筛选出出现次数最多的公众号
    # traverse_url_set = set()
    nickname_lst = []
    for recommend_d in data_lst:
        recommend_item_lst = list(recommend_d.values())[0]
        for recommend_item in recommend_item_lst:
            # if recommend_item['url'] not in traverse_url_set:
            #     traverse_url_set.add(recommend_item['url'])
            nickname_lst.append(recommend_item["nickname"])

    nc = Counter(nickname_lst)
    print(nc.most_common()[:high_frequency_value])

    high_frequency_nickname_lst = [
        k for k, freq in nc.most_common()[:high_frequency_value]
    ]

    # assert 1 == 2
    for recommend_d in data_lst:
        recommend_item_lst = list(recommend_d.values())[0]
        for recommend_item in recommend_item_lst:
            url_nickname_dict[recommend_item["url"]] = recommend_item["nickname"]

    res_lst = []
    for recommend_d in data_lst:
        url_k = list(recommend_d.keys())[0]
        recomment_lst = recommend_d[url_k]
        source_nickname = url_nickname_dict[url_k]
        # if source_nickname not in high_frequency_nickname_lst:
        #     continue

        res_lst.append(
            {
                "source": source_nickname,
                "target": {
                    recomment_item["nickname"]
                    for recomment_item in recomment_lst
                    if recomment_item["nickname"] in high_frequency_nickname_lst
                },
            }
        )

    source_set = set(map(lambda item: item["source"], res_lst))
    res_lst = merge_dict(source_set, res_lst)
    write_data(res_lst, fname.split(".pkl")[0] + "_graph.html")


def main():
    args = parser.parse_args()
    article_url = args.url
    nickname = args.nickname

    max_recursive = args.max_recursive
    high_frequency_value = args.high_frequency_value
    fname = "{}_{}.pkl".format(nickname, max_recursive)
    run(article_url, max_recursive=max_recursive, fname=fname)
    analysis(
        {article_url: nickname}, fname=fname, high_frequency_value=high_frequency_value
    )


if __name__ == "__main__":
    # nickname = '黑马青年'
    # article_url = 'https://mp.weixin.qq.com/s?__biz=MzUzNjk1NDIyNg==&mid=2247506248&idx=1&sn=c9a8b4d2e11fd1b6ae924877da3f0ea8&chksm=faeccd55cd9b44432ea81578b1e33db2ae5ce938ed5a90e32847cb0ea88916a16ac47c92e135&scene=132#wechat_redirect'

    # nickname = '大渝网'
    # article_url = 'https://mp.weixin.qq.com/s/4dm3DLlLjhR9eaK9c_BsBA'
    main()
