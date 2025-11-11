async def generate_image(visual_promt: str):
    url = f"https://image.pollinations.ai/prompt/{visual_promt.replace(' ', '%20')}?width=1920&height=1080&nologo=true"
    return url