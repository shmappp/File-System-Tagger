def extract_tags(tag_string):
    tags = tag_string.split(',')
    return [tag for tag in tags if len(tag) > 0]