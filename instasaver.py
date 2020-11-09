import re
import os
import tempfile
import instaloader
import base64
import streamlit as st

from fire import Fire
from zipfile import ZipFile

def main():
    st.title('Instasaver')
    st.markdown('Only for public profile')
    with tempfile.TemporaryDirectory() as temp:
        load = instaloader.Instaloader(
                dirname_pattern=temp,
                download_comments=False,
                download_geotags=False,
                download_video_thumbnails=False,
                save_metadata=False)

        selections = st.selectbox('Which one you want to download?', ['Download post', 'Download story', 'Download follower list', 'Download following list'])

        if selections == 'Download post':
            url_input = st.text_input('Url')
            
            try:
                if url_input:
                    load.post_metadata_txt_pattern = ''
                    shortcode = url_to_short_code(url_input)
                    check_post_url(load, shortcode, temp)
            
            except AttributeError:
                st.write("It seems like it's not a url")

            except KeyError:
                st.write("It seems like it's a private account")

        elif selections == 'Download story':
            username = st.text_input('Username')
            st.write("Download all the user stories (only public profile), if you try download private profile then it's only download user id")
            if username:
                try:
                    load.login('your_username', 'your_password') #you expect something mate?
                    profile = instaloader.Profile.from_username(load.context, username)
                    load.filename_pattern = '{date_utc}'
                    download_stories(load, username, profile, temp)

                except instaloader.ProfileNotExistsException:
                    st.write()

                except instaloader.ConnectionException:
                    st.write("There's some trouble, sorry about that. Try again later")

        elif selections == 'Download following list':
            username = st.text_input('Username')
            if username:
                try:
                    load.login('your_username', 'your_password') #you expect something mate?
                    profile = instaloader.Profile.from_username(load.context, username)
                    following_list(profile, username, temp)

                except instaloader.ProfileNotExistsException:
                    st.write()

                except instaloader.ConnectionException:
                    st.write("There's some trouble, sorry about that. Try again later")

        elif selections == 'Download follower list':
            username = st.text_input('Username')
            if username:
                try:
                    load.login('your_username', 'your_password') #you expect something mate?
                    profile = instaloader.Profile.from_username(load.context, username)
                    follower_list(profile, username, temp)

                except instaloader.ProfileNotExistsException:
                    st.write()

                except instaloader.ConnectionException:
                    st.write("There's some trouble, sorry about that. Try again later")

def url_to_short_code(post_url):
    regexp = '^(?:.*\/(p|tv)\/)([\d\w\-_]+)'
    post_short_code = re.search(regexp, post_url).group(2)
    print(f'From url {post_url} extracted shorcode:{post_short_code}')
    return post_short_code

def following_list(profile, user, temp):
    with open(f'{temp}/{profile.username}_following.txt', 'w') as f:
        for following in profile.get_followees():
            f.write(f'{following.username}\n')

    st.markdown(download_button(f'{temp}/{profile.username}_follower.txt', temp), unsafe_allow_html=True)

def follower_list(profile, user, temp):
    with open(f'{temp}/{profile.username}_follower.txt', 'w') as f:
        for follower in profile.get_followers():
            f.write(f'{follower.username}\n')

    st.markdown(download_button(f'{temp}/{profile.username}_follower.txt', temp), unsafe_allow_html=True)

def check_post_url(loader, shortcode, temp):
    post = instaloader.Post.from_shortcode(loader.context, shortcode)
    loader.download_post(post, target=temp)
    file_list = [filename for filename in os.listdir(temp)]
    if len(file_list) == 1:
        try:
            st.image(f'{temp}/{file_list[0]}', use_column_width=True)
            st.markdown(download_button(f'{temp}/{file_list[0]}', temp), unsafe_allow_html=True)

        except:
            st.video(f'{temp}/{file_list[0]}')
            st.markdown(download_button(f'{temp}/{file_list[0]}', temp), unsafe_allow_html=True)

    else:
        for i in file_list:
            try:
                st.image(f'{temp}/{i}', use_column_width=True)
                st.markdown(download_button(f'{temp}/{i}', temp), unsafe_allow_html=True)

            except:
                st.video(f'{temp}/{i}')
                st.markdown(download_button(f'{temp}/{i}', temp), unsafe_allow_html=True)

def download_stories(loader, user, profile, temp):
    profile_id = loader.check_profile_id(user)
    loader.download_stories(userids=[profile_id.userid])
    file_list = [filename for filename in os.listdir(temp)]

    with ZipFile(f'{temp}/{profile.username}_stories.zip', 'w') as zip:
        for filename in file_list:
            zip.write(f'{temp}/{filename}')

    st.markdown(download_button(f'{temp}/{profile.username}_stories.zip', temp), unsafe_allow_html=True)

def download_button(bin_file, temp):
    with open(bin_file, 'rb') as f:
        data = f.read()
        bin_str = base64.b64encode(data).decode()
        href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Download here</a>'
        return href

if __name__ == '__main__':
    Fire(main)
