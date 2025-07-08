import google.generativeai as genai
import os
from dotenv import load_dotenv
from datetime import datetime
from database import forum_db, user_db
from bson import ObjectId

load_dotenv()

class CommunityService:
    def __init__(self):
        """Initialize community service with Gemini AI for content moderation"""
        # Initialize Gemini AI
        google_api_key = os.getenv('GOOGLE_API_KEY')
        if google_api_key:
            genai.configure(api_key=google_api_key)
            self.genai_model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.genai_model = None

        # Forum categories
        self.categories = [
            'crop_management',
            'pest_control',
            'soil_health',
            'irrigation',
            'market_prices',
            'equipment',
            'weather_discussion',
            'success_stories',
            'questions_help',
            'general_discussion'
        ]

    def create_forum_post(self, user_id, title, content, category):
        """Create a new forum post with AI content analysis"""
        # Validate category
        if category not in self.categories:
            return {'error': 'Invalid category'}

        # AI content moderation
        moderation_result = self._moderate_content(title + " " + content)

        if moderation_result['is_appropriate']:
            # Create the post
            post_result = forum_db.create_post(user_id, title, content, category)

            return {
                'success': True,
                'post_id': str(post_result.inserted_id),
                'message': 'Post created successfully',
                'ai_suggestions': moderation_result.get('suggestions', [])
            }
        else:
            return {
                'success': False,
                'error': 'Content not appropriate for community guidelines',
                'reason': moderation_result.get('reason', 'Content policy violation')
            }

    def get_forum_posts(self, category=None, limit=20):
        """Get forum posts with enhanced information"""
        posts = forum_db.get_posts(category, limit)

        # Enhance posts with user information and AI insights
        enhanced_posts = []
        for post in posts:
            # Get user info (in a real app, you'd have user profiles)
            enhanced_post = {
                'id': str(post['_id']),
                'title': post['title'],
                'content': post['content'],
                'category': post['category'],
                'likes': post.get('likes', 0),
                'views': post.get('views', 0),
                'created_at': post['created_at'],
                'user_id': post['user_id'],
                'ai_summary': self._generate_post_summary(post['content'])
            }
            enhanced_posts.append(enhanced_post)

        return enhanced_posts

    def add_comment(self, post_id, user_id, content):
        """Add a comment to a forum post"""
        # AI content moderation
        moderation_result = self._moderate_content(content)

        if moderation_result['is_appropriate']:
            comment_result = forum_db.add_comment(post_id, user_id, content)
            return {
                'success': True,
                'comment_id': str(comment_result.inserted_id),
                'message': 'Comment added successfully'
            }
        else:
            return {
                'success': False,
                'error': 'Comment not appropriate for community guidelines'
            }

    def get_ai_farming_advice(self, question, category='general'):
        """Get AI-powered farming advice for community questions"""
        if not self.genai_model:
            return "AI advice service unavailable"

        prompt = f"""
        As an experienced agricultural advisor, provide helpful advice for this farming question:

        Category: {category}
        Question: {question}

        Please provide:
        1. Direct answer to the question
        2. Practical implementation steps
        3. Potential challenges and solutions
        4. Additional resources or considerations
        5. Regional considerations for South African farming

        Keep the advice practical, actionable, and suitable for farmers of all experience levels.
        """

        try:
            response = self.genai_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Unable to generate farming advice: {str(e)}"

    def get_trending_topics(self):
        """Get trending topics in the farming community"""
        if not self.genai_model:
            return "Trending topics unavailable"

        # Get recent posts
        recent_posts = forum_db.get_posts(limit=50)

        # Extract topics and content for analysis
        content_summary = ""
        for post in recent_posts[:10]:  # Analyze top 10 recent posts
            content_summary += f"Title: {post['title']}\nCategory: {post['category']}\n\n"

        prompt = f"""
        Based on recent farming community discussions, identify trending topics and themes:

        Recent Community Posts:
        {content_summary}

        Please identify:
        1. Top 5 trending farming topics
        2. Common challenges being discussed
        3. Popular crop types being mentioned
        4. Seasonal concerns
        5. Emerging opportunities or technologies

        Format as a brief summary suitable for a community dashboard.
        """

        try:
            response = self.genai_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Unable to analyze trending topics: {str(e)}"

    def get_expert_insights(self, topic):
        """Get expert insights on specific farming topics"""
        if not self.genai_model:
            return "Expert insights unavailable"

        prompt = f"""
        As a panel of agricultural experts, provide comprehensive insights on: {topic}

        Please cover:
        1. Current best practices
        2. Recent research and innovations
        3. Common mistakes to avoid
        4. Cost-benefit analysis
        5. Future trends and predictions
        6. Specific recommendations for South African conditions

        Provide expert-level depth while remaining accessible to practicing farmers.
        """

        try:
            response = self.genai_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Unable to generate expert insights: {str(e)}"

    def create_knowledge_base_entry(self, title, content, category, tags):
        """Create a knowledge base entry with AI enhancement"""
        if not self.genai_model:
            enhanced_content = content
        else:
            # Enhance content with AI
            prompt = f"""
            Enhance this farming knowledge base entry with additional useful information:

            Title: {title}
            Category: {category}
            Content: {content}

            Please add:
            1. Additional context and background
            2. Related best practices
            3. Common variations or alternatives
            4. Troubleshooting tips
            5. Related topics farmers should know

            Keep the original content and add value without changing the core message.
            """

            try:
                response = self.genai_model.generate_content(prompt)
                enhanced_content = content + "\n\n--- AI Enhanced Information ---\n" + response.text
            except Exception as e:
                enhanced_content = content

        # Save to database (you'd implement a knowledge base collection)
        knowledge_entry = {
            'title': title,
            'content': enhanced_content,
            'category': category,
            'tags': tags,
            'created_at': datetime.utcnow(),
            'views': 0,
            'helpful_votes': 0
        }

        return knowledge_entry

    def _moderate_content(self, content):
        """AI-powered content moderation"""
        if not self.genai_model:
            return {'is_appropriate': True, 'suggestions': []}

        prompt = f"""
        Review this content for a farming community forum:

        Content: {content}

        Check for:
        1. Inappropriate language or content
        2. Spam or promotional content
        3. Misinformation about farming practices
        4. Off-topic content

        Respond with:
        - "APPROPRIATE" if content is suitable
        - "INAPPROPRIATE" if content violates guidelines
        - Brief reason if inappropriate
        - Suggestions for improvement if needed
        """

        try:
            response = self.genai_model.generate_content(prompt)
            response_text = response.text.upper()

            is_appropriate = "APPROPRIATE" in response_text
            reason = response.text if not is_appropriate else None

            return {
                'is_appropriate': is_appropriate,
                'reason': reason,
                'suggestions': []
            }
        except Exception as e:
            # Default to allowing content if AI fails
            return {'is_appropriate': True, 'suggestions': []}

    def _generate_post_summary(self, content):
        """Generate AI summary for long posts"""
        if not self.genai_model or len(content) < 200:
            return None

        prompt = f"""
        Create a brief summary (1-2 sentences) of this farming forum post:

        {content[:500]}...

        Focus on the main topic and key points.
        """

        try:
            response = self.genai_model.generate_content(prompt)
            return response.text
        except Exception as e:
            return None

# Initialize community service
community_service = CommunityService()