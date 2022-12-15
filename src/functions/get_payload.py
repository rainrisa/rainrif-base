def get_payload(text):
  payload = text.split()
  del payload[0]
  return ' '.join(payload)