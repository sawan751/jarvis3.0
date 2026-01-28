# brain.py
from Backend.general_q import general
from Backend.realtime_q import realtime
from Backend.systemq import handle_system_query

def classify_query(text):
    """
    Fast keyword-based classification of queries into system, realtime, or general.
    Returns a list of matching categories ordered by priority.
    """
    text_lower = text.lower()
    matches = []

    # System keywords - related to system operations
    system_keywords = [
        'open', 'close','play', 'modify', 'volume', 'shutdown', 'restart', 'start', 'stop',
        'launch', 'run', 'execute', 'file', 'folder', 'directory', 'window',
        'application', 'program', 'browser', 'settings', 'control','search'
    ]

    # Realtime keywords - require live data
    realtime_keywords = [
        'time', 'date', 'weather', 'temperature', 'forecast', 'stock', 'price',
        'news', 'current', 'now', 'today', 'tomorrow', 'yesterday', 'live',
        'update', 'latest', 'real-time', 'clock', 'calendar', 'schedule'
    ]

    # Question indicators - suggest general queries
    question_indicators = [
        'what', 'how', 'why', 'when', 'where', 'who', 'tell me', 'explain',
        'about', 'is', 'are', 'do', 'does', 'can', 'could', 'would', 'should'
    ]

    # Check for system keywords
    has_system = any(keyword in text_lower for keyword in system_keywords)
    if has_system:
        matches.append("system")

    # Check for realtime keywords
    has_realtime = any(keyword in text_lower for keyword in realtime_keywords)
    if has_realtime:
        matches.append("realtime")

    # Check for general questions (if not already classified as realtime)
    has_questions = any(indicator in text_lower for indicator in question_indicators)
    if has_questions and not has_realtime:
        matches.append("general")

    # If no specific keywords found, default to general
    if not matches:
        matches.append("general")

    return matches

def brainQ(text):
    try:
        # First, check if the whole text contains system keywords
        whole_response = classify_query(text)
        has_system = "system" in whole_response
        
        if has_system:
            # Split the input text into multiple queries based on delimiters
            delimiters = [' and ', ' then ', '. ', '! ', '? ']
            queries = [text]
            for delimiter in delimiters:
                new_queries = []
                for q in queries:
                    new_queries.extend(q.split(delimiter))
                queries = new_queries
            
            # Remove empty strings and strip whitespace
            queries = [q.strip() for q in queries if q.strip()]
            
            results = []
            for query in queries:
                # Use fast keyword-based classification for each query
                response = classify_query(query)
                
                # Handle classification
                if "system" in response:
                    print(f"\n🔹 System task detected: {query}")
                    result = handle_system_query(query)
                    results.append(result)
                elif "general" in response:
                    print(f"\n🔹 General query detected: {query}")
                    result = general(query)
                    results.append(result)
                elif "realtime" in response:
                    print(f"\n🔹 Realtime query detected: {query}")
                    result = realtime(query)
                    if result:
                        results.append(result)
                    else:
                        result = general(query)
                        results.append(result)
                else:
                    results.append(f"Unknown query: {query}")
            
            return "\n".join(results)  # Join results into a single string for speaking
        else:
            # Treat as single query
            response = whole_response
            
            # Handle classification
            if "system" in response:
                print("\n🔹 System task detected")
                return handle_system_query(text)
            elif "general" in response:
                print("\n🔹 General query detected")
                return general(text)
            elif "realtime" in response:
                print("\n🔹 Realtime query detected")
                result = realtime(text)
                if result:
                    return result
                else:
                    return general(text)
            else:
                return f"Unknown query: {text}"

    except Exception as e:
        print(f"An error occurred: {e}")
        return None