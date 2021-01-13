import requests
import random
from botsettings import NUMBER_OF_USERS, MAX_POSTS_PER_USER, MAX_LIKES_PER_USER

SIGNUP_PATH = 'http://localhost:8000/socialnetwork/signup'
TOKEN_PATH = 'http://localhost:8000/socialnetwork/api/token'
CREATEPOST_PATH = 'http://localhost:8000/socialnetwork/post/new'
LIKEPOST_PATH = 'http://localhost:8000/socialnetwork/post/{id}/like'


def is_any_post_has_zero_likes(posts: dict) -> bool:
    for id in posts:
        if posts[id] == 0:
            return True
    
    return False


def user_w_max_posts(users: list) -> [dict]:
    if not users:
        return None
    
    winner = None
    for u in users:
        if u['num_likes'] < MAX_LIKES_PER_USER:
            if winner is None or len(u['posts']) > len(winner['posts']):
                winner = u

    return winner


def user_has_post_w_zero_likes(user: dict) -> bool:
    for post_id in user['posts']:
        if post_likes[post_id] == 0:
            return True
    
    return False
    
    
if __name__ == '__main__':

    # Create users
    global users
    users = []
    for num in range(NUMBER_OF_USERS):
        email = f'botuser{num}@gmail.com'
        password = f'verysecurepassword'
        
        r = requests.post(SIGNUP_PATH, data={'email': email, 'password': password})
        r_js = r.json()
        if not r_js.get('id'):
            if r_js.get('email') and r_js['email'][0] == 'user with this email already exists.':
                print(f"user with this email {email} already exists")
            else:
                print(f"can't sign up user with {email}", r_js)
                exit(1)
        
        r = requests.post(TOKEN_PATH, data={'email': email, 'password': password})
        
        r_json = r.json()
        if 'access' in r_json:
            print(f"got token for user {num}")
            users.append({
                'num': num,
                'access': r_json['access']
            })
        else:
            print(f"Can't get token for {email}", r.text)
            exit(1)

    # Create posts
    global post_likes
    post_likes = {}
    for u in users:
        u['posts'] = []
        u['num_likes'] = 0

        headers = {'Authorization': 'Bearer ' + u['access']}
        num_posts = random.randint(1, MAX_POSTS_PER_USER)
      
        for _ in range(num_posts):
            r = requests.post(CREATEPOST_PATH, headers=headers, json={'title':'Lazy dog', 'body': 'The quick brown fox jumps over the lazy dog'})
            post_id = r.json()['id']
            
            u['posts'].append(post_id)
            
            post_likes[post_id] = 0
        
        print(f"created {len(u['posts'])} posts for user {u['num']}")
            
    # Main loop
    iter = 0
    while is_any_post_has_zero_likes(post_likes):
        winner = user_w_max_posts(users)
        if not winner:
            print("All users reached maximum of likes")
            exit(0)
            
        headers = {'Authorization': 'Bearer ' + winner['access']}
        print(f"winner user num {winner['num']} (max posts and extra likes) ")
        if not winner:
            print("all users reached maximum of likes")
            break
        
        winner_num_likes = winner['num_likes']
        for u in users:
            if winner['num'] == u['num']:
                continue
                
            while user_has_post_w_zero_likes(u):
                post_id_num = random.randint(0,len(u['posts']) - 1)
                post_id = u['posts'][post_id_num]
                
                print(f"user {winner['num']} trying to like post of user {u['num']}, post id={post_id}")
                r = requests.get(LIKEPOST_PATH.format(id=post_id), headers=headers)
                r_js = r.json()
                if r_js.get('post_id') and r_js.get('likes'):
                    print('success')
                    winner['num_likes'] += 1
                    post_likes[post_id] += 1
                    
                    if winner['num_likes'] >= MAX_LIKES_PER_USER:
                        break
                        
                    if not is_any_post_has_zero_likes(post_likes):
                        print("No more posts has zero likes")
                        exit(0)
                else:
                    print(r_js)
            
        if winner['num_likes'] == winner_num_likes:
            print(f"user {winner['num']} has extra {MAX_LIKES_PER_USER - winner['num_likes']} likes and it's no more other user's posts to like")
            exit(0)

        
    print("No more posts has zero likes")
    exit(0)

