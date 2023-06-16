import json

with open('../articles.json', 'r') as f:
    all_articles = sorted([article['link'] for article in json.load(f) if 'martinfowler' in article['link']])
    de_duped_articles = sorted(set(all_articles))

print(len(all_articles))

with open('../articles_with_tags.json') as f:
    cleaned_articles = sorted([article['link'] for article in json.load(f) if 'martinfowler' in article['link']])
print(len(cleaned_articles))

# diff = set([x for x in all_articles if x not in cleaned_articles])
diff = set([x for x in all_articles if x not in de_duped_articles])
print(*diff, sep='\n')
print(len(diff))

dup = {x: all_articles.count(x) for x in all_articles if all_articles.count(x) > 1}
print(dup)