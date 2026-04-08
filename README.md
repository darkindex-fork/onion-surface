I developed Onion Surface, a keyword-based web search tool focused on discovering less visible and harder-to-find content on the clear web, including information related to the dark web that becomes accessible through standard search engines.

The tool operates using a .txt file containing user-defined keywords, where each line represents a search query. Users have full control over the search process by adding any keywords they want into this file. The keywords.txt file can be found in the uploads folder.

It processes these keywords and retrieves results from DuckDuckGo, enabling structured exploration of various topics.

The system is optimized using asynchronous execution to handle multiple queries efficiently and improve performance.

Key features:
- DuckDuckGo search integration
- Keyword-based scanning using .txt files (user-defined keywords)
- Asynchronous execution for faster results
- Result collection per keyword
- Export results to CSV
- Search history storage and management

The project is focused on OSINT and general web discovery, helping identify less accessible or less visible information available on the surface web.