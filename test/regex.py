import re

test_links_all = """
    'http://www.youtube.com/watch?v=5Y6HSHwhVlY',
    'http://www.youtube.com/watch?/watch?other_param&v=5Y6HSHwhVlY',
    'http://www.youtube.com/v/5Y6HSHwhVlY',
    'http://youtu.be/5Y6HSHwhVlY',
    'http://www.youtube.com/embed/5Y6HSHwhVlY?rel=0" frameborder="0"',
    'http://m.youtube.com/v/5Y6HSHwhVlY',
    'https://www.youtube-nocookie.com/v/5Y6HSHwhVlY?version=3&amp;hl=en_US',
    'http://www.youtube.com/',
    'http://www.youtube.com/?feature=ytca',
	 'http://www.youtube.com/kindafunny'
"""

test_links = """
    'http://www.youtube.com/watch?v=5Y6HSHwhVlY',
    'http://www.youtube.com/watch?/watch?other_param&v=5Y6HSHwhVlY',
    'http://www.youtube.com/v/5Y6HSHwhVlY',
    'http://youtu.be/5Y6HSHwhVlY',
    'http://www.youtube.com/test',
	 'http://www.youtube.com/kindafunny'
"""

pattern = r'(?:https?:\/\/)?(?:[0-9A-Z-]+\.)?(?:youtu|youtube-nocookie)\.(?:com|be)\/(?:watch\?v=|watch\?.+&v=|embed\/|v\/|.+\?v=)?([^&=\n%\?]{11})'

result = re.findall(pattern, test_links, re.MULTILINE | re.IGNORECASE)
print(result)
# final_result = list(set(result))
# print(final_result)