let accessToken: string | null = null;

export const tokenStorage = {
	setToken: (token: string) => {
		accessToken = token;
	},
	getToken: (): string | null => {
		return accessToken;
	},
	clearToken: () => {
		accessToken = null;
	},
};
