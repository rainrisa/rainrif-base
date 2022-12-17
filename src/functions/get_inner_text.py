def get_inner_text(text, entity):
  start = entity.offset
  end = start + entity.length

  return text[start:end]