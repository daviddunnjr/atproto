from flask import Flask, render_template, request, redirect, url_for
from atproto_service import get_profile, update_profile, get_posts, get_current_user_handle, create_post

app = Flask(__name__)

@app.route('/')
def home():
    return profile()

@app.route('/profile')
@app.route('/profile/<handle>')
def profile(handle=None):
    try:
        profile = get_profile(handle)
        posts = get_posts(handle)
        # Add embed type flags to posts
        for post in posts:
            post.has_images = False
            post.has_external = False
            post.has_quote = False
            post.quoted_post = None
            if post.post.record.embed:
                if hasattr(post.post.record.embed, 'images'):
                    post.has_images = True
                if hasattr(post.post.record.embed, 'external'):
                    post.has_external = True
                if hasattr(post.post.record.embed, 'quote'):
                    post.has_quote = True
                    # Extract quoted post information
                    try:
                        quote_obj = post.post.record.embed.quote
                        quoted_author = 'Unknown'
                        quoted_text = ''
                        quoted_created = ''
                        
                        # The quote object contains the referenced post
                        # Try to get author from various levels
                        if hasattr(quote_obj, 'author') and quote_obj.author:
                            author_obj = quote_obj.author
                            if hasattr(author_obj, 'display_name') and author_obj.display_name:
                                quoted_author = author_obj.display_name
                            elif hasattr(author_obj, 'handle'):
                                quoted_author = author_obj.handle
                        
                        # Try to get text from value/record
                        if hasattr(quote_obj, 'value') and quote_obj.value:
                            if hasattr(quote_obj.value, 'text'):
                                quoted_text = quote_obj.value.text
                            if hasattr(quote_obj.value, 'created_at'):
                                quoted_created = quote_obj.value.created_at
                        elif hasattr(quote_obj, 'record') and quote_obj.record:
                            if hasattr(quote_obj.record, 'text'):
                                quoted_text = quote_obj.record.text
                            if hasattr(quote_obj.record, 'created_at'):
                                quoted_created = quote_obj.record.created_at
                        elif hasattr(quote_obj, 'text'):
                            quoted_text = quote_obj.text
                            if hasattr(quote_obj, 'created_at'):
                                quoted_created = quote_obj.created_at
                        
                        post.quoted_post = {
                            'author': quoted_author,
                            'text': quoted_text,
                            'created_at': quoted_created
                        }
                    except Exception as e:
                        print(f"Error extracting quote post: {e}")
                        print(f"Quote embed object: {post.post.record.embed.quote}")
                        import traceback
                        traceback.print_exc()
            # Add context flags
            post.repost_author = None
            if post.reason and hasattr(post.reason, 'repost') and post.reason.repost and post.reason.by:
                post.repost_author = post.reason.by.display_name or post.reason.by.handle
            post.reply_author = None
            if post.reply and post.reply.parent and hasattr(post.reply.parent, 'author'):
                post.reply_author = post.reply.parent.author.display_name or post.reply.parent.author.handle
        # Determine if this is the authenticated user's profile
        current_user_handle = get_current_user_handle()
        is_own_profile = profile.handle.lower() == current_user_handle.lower()
        return render_template('profile.html', profile=profile, posts=posts, is_own_profile=is_own_profile)
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/edit_profile')
def edit_profile():
    try:
        profile = get_profile()
        return render_template('edit_profile.html', profile=profile)
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile_route():
    if request.method == 'POST':
        new_display_name = request.form.get('display_name')
        new_description = request.form.get('description')
        if new_display_name or new_description:
            try:
                update_profile(display_name=new_display_name, description=new_description)
                return redirect(url_for('profile'))
            except Exception as e:
                return f"Error updating profile: {str(e)}"
        else:
            return "No changes provided", 400
    else:
        # If GET, redirect back to profile
        return redirect(url_for('profile'))

@app.route('/new_post', methods=['POST'])
def new_post():
    try:
        text = request.form.get('text', '').strip()
        if not text:
            return "Post text cannot be empty", 400
        create_post(text)
        return redirect(url_for('profile'))
    except Exception as e:
        return f"Error creating post: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)