from instaloader import Instaloader, Profile, Post
import xlsxwriter
import os

SHORTCODE = 'CTjr7nip4Xo'

# <editor-fold desc="USERNAME PASSWORD">
ID = 'bakar_gas'
PASSWORD = 'gultom159159'
# </editor-fold>

L = Instaloader(download_pictures=False,
                download_video_thumbnails=False,
                download_videos=False,
                download_geotags=False,
                download_comments=True,
                save_metadata=False)

L.login(ID,PASSWORD)

thislist = []
post = Post.from_shortcode(L.context, SHORTCODE)
username = post.owner_username

for comments in post.get_comments():
    #if(len(thislist)<2500):
        thislist.append(comments.text)
    #else:
    #    break

path = username
if not os.path.exists(path):
    os.mkdir(path)
os.chdir(path)

workbook = xlsxwriter.Workbook('{}.xlsx'.format(SHORTCODE))
worksheet = workbook.add_worksheet()

col = 0
for row,data in enumerate(thislist):
    worksheet.write(row, col, data)
workbook.close()