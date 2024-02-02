# hacker-newd
Python script for analyzing Hacker News

I've read Hacker News for many years, and I've noticed every once in a while an interesting story very quickly drops off the front page, despite the post having a large number of upvotes in a relatively short time period. I've been curious as to what stories I may be missing in the gaps between HN visits, which is why I wrote this tool.

This tool effectively undoes all the artificial modifiers to rank, and sorts stories based purely on points over time. It predicts where a story would be on the front page if it wasn't being modified by "other factors" including:

> user flags, anti-abuse software, software which demotes overheated discussions, account or site weighting, and moderator action (from [HN FAQ](https://news.ycombinator.com/newsfaq.html))

It also compares the predicted and actual rank to look for recent stories that are significantly higher or lower rank than expected.

**Important!** I'm not against moderation, it's good that Hacker News is moderated, the site would be very different otherwise. Dramatic, controversial stories about business and politics would start to drown out stories on programming, science and engineering. I think the HN mods do a good job, and this isn't meant to accuse them of anything.

**Disclaimer:** This tool does not use the actual HN ranking algorithm, it's a secret as far as I know, and this tool cannot tell if or why a post has actually been "down-ranked" or "up-ranked". 

**Personal rant:**  I strongly believe that there's active abuse of reporting systems on nearly every social network, including Hacker News. The abuse comes from individuals with religious/political agendas, state actors looking to bury certain stories, and online reputation management (ORM) companies. While HN mods are able to combat this for the most part, it's impossible to investigate every occurrence and often difficult to distinguish between legitimate reports versus actual abuse.

## Usage

```
python hacker-newd.py
```

A web page should open automatically after it's done fetching data from the HN Firebase API. 
