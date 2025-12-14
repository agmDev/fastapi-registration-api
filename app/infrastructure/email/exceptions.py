class EmailProviderError(Exception):
    pass


class EmailProviderUnavailable(EmailProviderError):
    pass
