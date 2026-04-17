import json

new_data = {
    "updated": "2026-04-17T10:30:00",
    "source_url": "https://understandingwar.org/research/middle-east/iran-update-special-report-april-16-2026/",
    "current_report": {
        "url": "https://understandingwar.org/research/middle-east/iran-update-special-report-april-16-2026/",
        "title": "Iran Update Special Report, April 16, 2026",
        "title_zh": "伊朗局势更新特别报告 - 2026年4月16日",
        "date": "2026-04-16",
        "takeaways": [
            {
                "en": "Iran is leveraging its position over the Strait of Hormuz to extract concessions while maintaining its claim to control access to the waterway. Iran has proposed allowing ships to transit through the Omani side of the Strait of Hormuz without interference if the United States agrees to conditions that prevent renewed conflict and meet Iranian demands, including unfreezing Iranian funds and a permanent end to US and Israeli strikes.",
                "zh": "【伊朗利用霍尔木兹海峡地位索取让步】伊朗提议允许船只不受干扰地通过霍尔木兹海峡阿曼一侧，条件是美方同意防止冲突重启并满足伊朗要求，包括解冻伊朗资金和永久停止美以打击。ISW警告称，接受此类要求将向伊朗表明，其现在和未来都可以利用霍尔木兹海峡胁迫美国。"
            },
            {
                "en": "The main sticking point in current US-Iran negotiations is reportedly Iran's enrichment of uranium and its highly enriched uranium stockpile. The United States has proposed a 20-year pause to enrichment, while the Iranians offered a 3- to 5-year pause. The United States wants Iran to remove all of the highly enriched uranium from Iran, whereas Iran reportedly wants to keep some of it.",
                "zh": "【美伊谈判症结：铀浓缩暂停年限】当前美伊谈判的主要症结是铀浓缩和高浓缩铀库存问题。美方要求暂停至少20年，伊朗则提出3-5年暂停方案——这已是伊朗的重要让步，但仍与美方要求存在显著差距。"
            },
            {
                "en": "The IRGC appears to be playing an outsized role in Iranian decision-making in these negotiations, traditionally meant for civilian leadership. Pakistani Army Chief Field Marshall Asim Munir met with Iran's negotiating delegation lead Parliament Speaker Mohammad Bagher Ghalibaf, and Iran's Khatam ol Anbia Central Headquarters Commander Major General Ali Abdollahi Aliabadi on April 16 as part of his mediation mission in Tehran.",
                "zh": "【IRGC在谈判中扮演过大角色】革命卫队在传统上应由文职领导人主导的谈判中扮演了过大角色。巴基斯坦陆军参谋长阿西姆·穆尼尔元帅4月16日在德黑兰会见了伊朗谈判代表团团长议长加利巴夫，以及Khatam ol Anbia中央总部指挥官阿卜杜拉希·阿里阿巴迪少将——后者通常不负责外交使命，而是负责联合作战。"
            },
            {
                "en": "US President Donald Trump stated on April 16 that the United States is 'very close' to reaching a deal with Iran. Trump stated that Iran 'has agreed to almost everything' and added that Iran has agreed to hand over its enriched uranium stockpile. Trump added that he may travel to Pakistan to sign an agreement if negotiations conclude in Islamabad.",
                "zh": "【特朗普称美伊'非常接近'达成协议】特朗普4月16日表示，伊朗'已同意几乎所有事情'，包括交出浓缩铀库存。他称若谈判在伊斯兰堡敲定，他可能亲赴巴基斯坦签署协议。但伊朗尚未公开确认特朗普的说法。"
            },
            {
                "en": "The United States Navy continues to enforce a blockade on Iranian ports. Chairman of the Joint Chiefs of Staff Dan Caine and Defense Secretary Pete Hegseth defined a blockade line that runs diagonally across the Gulf of Iran from Ras al Hadd, Oman, to the Iran-Pakistan border. CENTCOM announced that the blockade has effectively halted maritime trade to and from Iran.",
                "zh": "【美军封锁已有效停止伊朗海上贸易】美军继续执行对伊朗港口的封锁。参谋长联席会议主席凯恩和国防部长赫格塞思划定了一条从阿曼拉斯哈德到伊朗-巴基斯坦边境的对角线封锁线。CENTCOM宣布，封锁已有效停止伊朗的进出口海上贸易。"
            },
            {
                "en": "The Iranian missile force is exploiting the current ceasefire to reconstitute its tactical and operational-level units, but rebuilding the industrial facilities and other components that sustain the missile force at the strategic level will be extremely challenging. Iran has begun to dig up its missile launchers but has not determined how to 'replenish' its missile stockpile.",
                "zh": "【伊朗导弹部队利用停火重建战术单位】伊朗已开始挖掘被掩埋的导弹发射器，试图恢复战术和作战级单位的协调能力。但在战略层面，重建被空袭摧毁的导弹工业设施（从最终组件装配到铝钢厂）将极其困难，所需时间远超2025年6月打击后的恢复期。"
            },
            {
                "en": "US President Donald Trump announced that Lebanon and Israel have agreed to a 10-day ceasefire beginning at 5:00 PM ET on April 16. The US State Department published six provisions for the Israel-Lebanon ceasefire agreement, including that Israel agrees to halt all offensive military operations in Lebanon and the Lebanese government agrees to take meaningful steps to prevent Hezbollah attacks.",
                "zh": "【以黎达成10天临时停火】特朗普宣布以色列和黎巴嫩同意自美东时间4月16日下午5时起实施为期10天的停火。美国务院公布了六项条款，包括以色列停止在黎巴嫩的进攻性军事行动，黎巴嫩政府采取有意义步骤防止真主党袭击等。"
            },
            {
                "en": "Iranian Foreign Affairs Minister Abbas Araghchi called his Chinese counterpart Wang Yi on April 15, likely in part to discuss the ongoing blockade in the Strait of Hormuz. Yi affirmed Iran's 'rights and interests' in the Strait of Hormuz 'must be respected and protected.' The PRC may be concerned with the blockade's effect on its ability to get Iranian oil.",
                "zh": "【伊朗外长与中国外长通话讨论霍尔木兹封锁】伊朗外长阿拉格齐4月15日与中方王毅通话，感谢中方'缓和紧张局势的努力'。王毅表示伊朗在霍尔木兹海峡的'权益必须得到尊重和保护'。中国约13.4%的海上进口石油来自伊朗，对封锁影响其能源供应深感关切。"
            }
        ],
        "charts": [
            {
                "url": "https://understandingwar.org/wp-content/uploads/2026/04/Traffic-Through-the-Strait-of-Hormuz-April-16-2026.webp",
                "title_zh": "霍尔木兹海峡通行情况（4月16日）",
                "context": [
                    "4月15日下午2点至4月16日下午2点海峡通航数据",
                    "商业航运在封锁下的有限活动",
                    "至少4艘船只进入海峡，2艘离开"
                ]
            },
            {
                "url": "https://understandingwar.org/wp-content/uploads/2026/04/Hezbollah-Attacks-in-Northern-Israel-and-Southern-Lebanon-between-April-15-2026-at-2PM-ET-and-April-16-2026-at-2PM-ET.webp",
                "title_zh": "真主党在以色列和黎巴嫩的袭击（4月15-16日）",
                "context": [
                    "以黎停火生效前真主党发动的30次以色列北部袭击",
                    "以军在黎巴嫩南部的37次真主党攻击声称",
                    "停火前的最后激战态势"
                ]
            }
        ]
    },
    "history": [
        {"date": "2026-04-16", "title": "Iran Update Special Report, April 16, 2026", "url": "https://understandingwar.org/research/middle-east/iran-update-special-report-april-16-2026/"},
        {"date": "2026-04-15", "title": "Iran Update Special Report, April 15, 2026", "url": "https://understandingwar.org/research/middle-east/iran-update-special-report-april-15-2026/"},
        {"date": "2026-04-14", "title": "Iran Update Special Report, April 14, 2026", "url": "https://understandingwar.org/research/middle-east/iran-update-special-report-april-14-2026/"},
        {"date": "2026-04-13", "title": "Iran Update Special Report, April 13, 2026", "url": "https://understandingwar.org/research/middle-east/iran-update-special-report-april-13-2026/"},
        {"date": "2026-04-12", "title": "Iran Update Special Report, April 12, 2026", "url": "https://understandingwar.org/research/middle-east/iran-update-special-report-april-12-2026/"},
        {"date": "2026-04-11", "title": "Iran Update Special Report, April 11, 2026", "url": "https://understandingwar.org/backgrounder/iran-update-special-report-april-11-2026"},
        {"date": "2026-04-10", "title": "Iran Update Special Report, April 10, 2026", "url": "https://understandingwar.org/backgrounder/iran-update-special-report-april-10-2026"}
    ]
}

with open('isw_data_april16.json', 'w', encoding='utf-8') as f:
    json.dump(new_data, f, ensure_ascii=False, indent=2)

print('JSON saved')
