text = """
CrowdStrike(https://www.crowdstrike.com/en-us/) Threat Hunting Report 2024 highlights the increase in living off the land exploits, insider threats, identity compromise, and cloud-specific threats as modern adversaries evolve to bypass traditional security solutions.

At Fal.Con 2024 (September 16-19 in Las Vegas), Arsen Darakdjian, Senior Vice President of Global Cybersecurity from Paramount, will join Suril Desai, our VP of Detection Engineering, in a breakout session(https://mktoab560139.com/) to discuss how technological innovations in deception technology are enabling security teams to defend against these stealthy threats.

Read this blog to learn about this session and the role of cyber deception in the evolving threat landscape.
"""

# 1、输出text中所有的单词，并统一规约成小写形式
# 2、输出text中的所有网址
# 3、给定一个词threat，忽略大小写，计算其在text中出现的次数和对应的位置，位置序号从0开始

# 答案参考：

import re

text = """
CrowdStrike(https://www.crowdstrike.com/en-us/) Threat Hunting Report 2024 highlights the increase in living off the land exploits, insider threats, identity compromise, and cloud-specific threats as modern adversaries evolve to bypass traditional security solutions.

At Fal.Con 2024 (September 16-19 in Las Vegas), Arsen Darakdjian, Senior Vice President of Global Cybersecurity from Paramount, will join Suril Desai, our VP of Detection Engineering, in a breakout session(https://mktoab560139.com/) to discuss how technological innovations in deception technology are enabling security teams to defend against these stealthy threats.

Read this blog to learn about this session and the role of cyber deception in the evolving threat landscape.
"""

# 1. Extract all words and normalize to lowercase
words = re.findall(r"[A-Za-z]+", text)
words_lower = [w.lower() for w in words]

# 2. Extract all URLs
urls = re.findall(r"https?://[^\s\)]+", text)

# 3. Count occurrences of 'threat' and positions
positions = [i for i, w in enumerate(words_lower) if w == 'threat']
count = len(positions)

print("所有单词（小写）：", words_lower)
print("\n所有网址：", urls)
print(f"\n单词 'threat' 出现次数: {count}")
print("出现位置（从0开始）：", positions)

