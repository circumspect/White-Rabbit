def get_text_channels(guild):
    return {
        channel.name: channel
        for channel in guild.text_channels
    }