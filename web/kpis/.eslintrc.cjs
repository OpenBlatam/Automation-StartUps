module.exports = {
	env: { node: true, es2022: true },
	extends: [
		'eslint:recommended',
		'plugin:@typescript-eslint/recommended',
		'plugin:import/recommended',
		'plugin:import/typescript',
		'prettier',
	],
	parser: '@typescript-eslint/parser',
	parserOptions: { ecmaVersion: 'latest', sourceType: 'module', project: false },
	plugins: ['@typescript-eslint', 'import'],
	rules: {
		'@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
		'import/order': [
			'warn',
			{ groups: ['builtin', 'external', 'internal', 'parent', 'sibling', 'index'], 'newlines-between': 'always' },
		],
	},
};




