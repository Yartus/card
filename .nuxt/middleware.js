const middleware = {}

middleware['auth-check'] = require('../middleware/auth-check.js')
middleware['auth-check'] = middleware['auth-check'].default || middleware['auth-check']

export default middleware
