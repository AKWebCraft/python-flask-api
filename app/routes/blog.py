from flask import Blueprint, request, jsonify
from ..models import Blog
from ..utils import token_required
from .. import db

blog_bp = Blueprint('blog', __name__)



#GET ALL BLOGS
@blog_bp.route('/', methods=['GET'])
def get_all_blogs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 2, type=int) 

    blogs_paginated = Blog.query.paginate(page=page, per_page=per_page, error_out=False)

    if blogs_paginated.items:
        
        blogs_list = []
        for blog in blogs_paginated.items:
            blog_data = {
                'id': blog.id,
                'title': blog.title,
                'content': blog.content,
                'author_id': blog.author_id,
            }
            blogs_list.append(blog_data)

        pagination_info = {
            'total_blogs': blogs_paginated.total,
            'total_pages': blogs_paginated.pages,
            'current_page': blogs_paginated.page,
            'blogs_per_page': blogs_paginated.per_page,
        }

        return jsonify({
            'blogs': blogs_list,
            'pagination': pagination_info
        }), 200

    else:
        return jsonify({'message': 'No blogs found!'}), 404



#CREATE BLOG
@blog_bp.route('/create', methods=['POST'])
@token_required
def create_blog(current_user):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        title = data.get('title')
        content = data.get('content')
        
        if not title or not content:
            return jsonify({'error': 'Title and content are required'}), 400
        
        if len(title) > 255:
            return jsonify({'error': 'Title must be less than 255 characters'}), 400
        
        new_blog = Blog(title=title, content=content, author_id=current_user.id)
        db.session.add(new_blog)
        db.session.commit()
        
        return jsonify({'message': 'Blog created successfully!', 'blog': {
            'id': new_blog.id,
            'title': new_blog.title,
            'content': new_blog.content,
            'author_id': new_blog.author_id
        }}), 201  
    
    except KeyError as e:
        return jsonify({'error': f'Missing key: {str(e)}'}), 400
    except Exception as e:
        print(f"Error creating blog: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500
    
    
#GET SINGLE BLOG   
@blog_bp.route('/<int:blog_id>', methods=['GET'])
def get_blog(blog_id):
    try:
        blog = Blog.query.get(blog_id)
        
        if not blog:
            return jsonify({'message': 'Blog not found!'}), 404

        return jsonify({
            'id': blog.id,
            'title': blog.title,
            'content': blog.content,
            'author_id': blog.author_id,
        }), 200

    except Exception as e:
        print(f"Error retrieving blog: {e}")
        return jsonify({'message': 'An unexpected error occurred.'}), 500
    



#UPDATE BLOG
@blog_bp.route('/<int:blog_id>', methods=['PUT'])
@token_required
def edit_blog(current_user, blog_id):
    blog = Blog.query.get(blog_id)
    if not blog:
        return jsonify({'message': 'Blog not found!'}), 404
    if blog.author_id != current_user.id:
        return jsonify({'message': 'You are not authorized to edit this blog!'}), 403

    data = request.get_json()
    blog.title = data['title']
    blog.content = data['content']
    db.session.commit()
    return jsonify({'message': 'Blog updated successfully!'})


#SEARCH BLOG
@blog_bp.route('/search', methods=['GET'])
def search_blog_by_title():
    query = request.args.get('q', '') 
    
    if not query:
        return jsonify({'message': 'Please provide a search query'}), 400
    
    blogs = Blog.query.filter(Blog.title.ilike(f'%{query}%')).all()

    if blogs:
        results = [{'id': post.id, 'title': post.title, 'content': post.content} for post in blogs]
        return jsonify({'results': results}), 200
    else:
        return jsonify({'message': 'No blog posts found'}), 404


