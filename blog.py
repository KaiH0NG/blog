import streamlit as st
import hashlib
import base64
from io import BytesIO
from PIL import Image
import uuid

# 设置管理员密码（请将此密码改为您自己的安全密码）
ADMIN_PASSWORD = "your_secure_password_here"

# 自定义主题
def set_custom_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans SC', sans-serif;
    }
    
    .stApp {
        background-color: #e6f2ff;
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    h1 {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: #0066cc !important;
    }
    
    h2 {
        font-size: 1.8rem !important;
        font-weight: 500 !important;
        color: #0066cc !important;
    }
    
    .stButton>button {
        background-color: #0066cc;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-size: 1rem;
        font-weight: 500;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #0052a3;
    }
    
    .blog-post {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .blog-post h3 {
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        color: #0066cc !important;
        margin-bottom: 0.5rem;
    }
    
    .blog-post p {
        color: #333;
        line-height: 1.5;
    }

    .category-tag {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        background-color: #b3d9ff;
        color: #0066cc;
        border-radius: 5px;
        font-size: 0.8rem;
        margin-bottom: 0.5rem;
    }

    .delete-button {
        color: #ff4d4d;
        cursor: pointer;
        float: right;
    }

    .delete-button:hover {
        color: #ff1a1a;
    }

    .comment {
        background-color: #f0f8ff;
        border-radius: 5px;
        padding: 0.5rem;
        margin-top: 0.5rem;
    }

    .comment-author {
        font-weight: bold;
        color: #0066cc;
    }

    .user-menu {
        position: fixed;
        top: 0.5rem;
        right: 1rem;
        z-index: 1000;
    }

    .user-menu .stButton>button {
        background-color: transparent;
        color: #0066cc;
        border: 1px solid #0066cc;
        padding: 0.3rem 0.7rem;
        font-size: 0.9rem;
    }

    .user-menu .stButton>button:hover {
        background-color: #0066cc;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(password, hashed_password):
    return hash_password(password) == hashed_password

def check_admin():
    """返回`True` 如果用户是管理员"""
    return st.session_state.get('is_admin', False)

def admin_login():
    password = st.text_input("管理员密码", type="password", key="admin_password")
    if st.button("管理员登录", key="admin_login"):
        if check_password(password, hash_password(ADMIN_PASSWORD)):
            st.session_state.is_admin = True
            st.success("管理员登录成功!")
        else:
            st.error("密码错误")

def user_auth():
    login_tab, register_tab = st.tabs(["登录", "注册"])
    
    with login_tab:
        username = st.text_input("用户名", key="login_username")
        password = st.text_input("密码", type="password", key="login_password")
        if st.button("用户登录", key="user_login"):
            if username in st.session_state.users and check_password(password, st.session_state.users[username]['password']):
                st.session_state.user = username
                st.session_state.show_auth = False
                st.success("登录成功!")
            else:
                st.error("用户名或密码错误")
    
    with register_tab:
        new_username = st.text_input("用户名", key="register_username")
        new_password = st.text_input("密码", type="password", key="register_password")
        if st.button("注册", key="user_register"):
            if new_username and new_password:
                if new_username not in st.session_state.users:
                    st.session_state.users[new_username] = {'password': hash_password(new_password)}
                    st.success("注册成功!请登录")
                else:
                    st.error("用户名已存在")
            else:
                st.error("请填写用户名和密码")

def add_new_post():
    st.header("发布新文章")
    with st.form("new_post_form"):
        title = st.text_input("文章标题")
        category = st.selectbox("选择专题", ["影评", "日常", "观察"])
        content = st.text_area("文章内容")
        image = st.file_uploader("上传图片", type=["png", "jpg", "jpeg"])
        submit_button = st.form_submit_button("发布")
        
        if submit_button:
            if title and content:
                image_data = None
                if image:
                    image_data = base64.b64encode(image.getvalue()).decode()
                st.session_state.posts.append({
                    "id": str(uuid.uuid4()),
                    "title": title,
                    "category": category,
                    "content": content,
                    "image": image_data,
                    "comments": []
                })
                st.success("文章发布成功!")
            else:
                st.error("请填写标题和内容!")

def delete_post(post_id):
    st.session_state.posts = [post for post in st.session_state.posts if post['id'] != post_id]
    st.success("文章删除成功!")

def add_comment(post_id, comment):
    for post in st.session_state.posts:
        if post['id'] == post_id:
            post['comments'].append({"author": st.session_state.user, "content": comment})
            break

def main():
    st.set_page_config(page_title="我的博客", layout="wide")
    set_custom_theme()

    # Initialize session state
    if 'users' not in st.session_state:
        st.session_state.users = {}
    if 'posts' not in st.session_state:
        st.session_state.posts = [
            {"id": str(uuid.uuid4()), "title": "《盗梦空间》：梦境与现实的迷离交织", "category": "影评", "content": "克里斯托弗·诺兰导演的《盗梦空间》是一部令人深思的科幻杰作。影片探讨了现实与梦境的界限，以及人类潜意识的复杂性...", "image": None, "comments": []},
            {"id": str(uuid.uuid4()), "title": "春日漫步", "category": "日常", "content": "今天，我决定利用这个阳光明媚的周末去公园散步。春天的气息扑面而来，树上的新芽、地上的小花，都在诉说着生命的活力...", "image": None, "comments": []},
            {"id": str(uuid.uuid4()), "title": "城市中的孤独", "category": "观察", "content": "在这个繁忙的都市中，我常常观察到一种普遍存在的现象：人们虽然身处人群之中，却似乎比以往任何时候都更加孤独...", "image": None, "comments": []},
        ]
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False
    if 'show_auth' not in st.session_state:
        st.session_state.show_auth = False

    # User menu in the top right corner
    with st.container():
        st.markdown('<div class="user-menu">', unsafe_allow_html=True)
        if st.session_state.user:
            st.button(f"👤 {st.session_state.user}", key="user_menu")
            if st.button("登出", key="logout"):
                st.session_state.user = None
                st.session_state.is_admin = False
        else:
            if st.button("登录/注册", key="login_register"):
                st.session_state.show_auth = True
        st.markdown('</div>', unsafe_allow_html=True)

    # Title
    st.title("我的博客")
    st.markdown("<h2 style='text-align: center; color: #0066cc;'>分享影评、日常生活和独特观察</h2>", unsafe_allow_html=True)

    # User authentication
    if not st.session_state.user and st.session_state.show_auth:
        with st.expander("登录/注册", expanded=True):
            user_auth()

    # Admin login (hidden in expander)
    with st.expander("管理员登录", expanded=False):
        admin_login()

    # 只有管理员才能发布新文章
    if check_admin():
        add_new_post()

    # Blog posts section
    st.header("最新文章")

    # 添加专题筛选
    category_filter = st.selectbox("选择专题", ["全部", "影评", "日常", "观察"])

    for post in st.session_state.posts:
        if category_filter == "全部" or post["category"] == category_filter:
            with st.container():
                st.markdown(f"""
                <div class="blog-post">
                    <div class="category-tag">{post["category"]}</div>
                    <h3>{post["title"]}</h3>
                    <p>{post["content"]}</p>
                </div>
                """, unsafe_allow_html=True)
                if post["image"]:
                    image = Image.open(BytesIO(base64.b64decode(post["image"])))
                    st.image(image, use_column_width=True)
                
                # 显示评论
                st.write("评论:")
                for comment in post["comments"]:
                    st.markdown(f"""
                    <div class="comment">
                        <span class="comment-author">{comment['author']}:</span> {comment['content']}
                    </div>
                    """, unsafe_allow_html=True)
                
                # 添加评论
                if st.session_state.user:
                    comment = st.text_input("添加评论", key=f"comment_{post['id']}")
                    if st.button("发表评论", key=f"submit_comment_{post['id']}"):
                        add_comment(post['id'], comment)
                else:
                    st.info("请登录后发表评论")

                if check_admin():
                    if st.button(f"删除文章 '{post['title']}'", key=f"delete_{post['id']}"):
                        delete_post(post['id'])

    # Footer
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: #0066cc;'>© 2023 我的博客。保留所有权利。</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()