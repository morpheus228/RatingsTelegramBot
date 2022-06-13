messages_according_adding_status = {
    'successfully': lambda name: f'✅ Объект {name.upper()} успешно добавлен',
    'already added': lambda name: f'⏪ Объект {name.upper()} уже был добавлен',
    'deactivated': lambda name: f'❌ Объект {name.upper()} не существует.',
    'does not satisfy filters':  lambda name: f'🚫 Объект {name.upper()} не подходит под условия.',
    'error': lambda name: f'❌ Объект {name.upper()} не удалось добавить.'
}