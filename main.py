import instaloader

profile = instaloader.Profile.from_username(
    instaloader.Instaloader().context,
    "gardeshgari_sarina"
)

post = next(profile.get_posts())

print("Post found!")
print("Code:", post.shortcode)
print("Video:", post.is_video)
print("Caption:", post.caption)