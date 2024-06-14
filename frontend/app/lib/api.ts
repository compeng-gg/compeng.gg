'use client';

export const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v0/';
export const jwtObtainPairEndpoint = 'auth/login/'
export const jwtRefreshEndpoint = 'auth/refresh/'

export function fetchApiSingle(endpoint: string, token?: string): Promise<Response>;
export function fetchApiSingle(endpoint: string, data: object, token?: string): Promise<Response>;

export function fetchApiSingle(endpoint: string, dataOrToken?: object | string, maybeToken?: string): Promise<Response> {
  const url = apiUrl + endpoint

  let headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  let data: object | undefined;

  /* Single argument */
  if (typeof dataOrToken === "string") {
    headers['Authorization'] = `Bearer ${dataOrToken}`;
  }
  /* Both arguments */
  else {
    data = dataOrToken;
    if (maybeToken) {
      headers['Authorization'] = `Bearer ${maybeToken}`;
    }
  }

  if (data) {
    return fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(data),
    });
  } else {
    return fetch(url, {
      method: 'GET',
      headers,
    });
  }
}

export function fetchApi(jwt: any, setAndStoreJwt:any, url: string): Promise<Response>;
export function fetchApi(jwt: any, setAndStoreJwt:any, url: string, data: object): Promise<Response>;

export async function fetchApi(jwt: any, setAndStoreJwt:any, endpoint: string, data?: object): Promise<any> {
  let response: Response;
  if (data === undefined) {
    response = await fetchApiSingle(endpoint, jwt.access);
  }
  else {
    response = await fetchApiSingle(endpoint, data, jwt.access);
  }

  if (response.status !== 401) {
    return response
  }
  else if (jwt.access === undefined) {
    setAndStoreJwt(undefined);
    return response
  }

  /* Need to refesh the access token */
  let accessToken = undefined;
  try {
    const refreshToken: string = jwt.refresh
    const refreshResponse: Response = await fetchApiSingle(jwtRefreshEndpoint, {'refresh': refreshToken});
    const refreshData: any = await refreshResponse.json();
    accessToken = refreshData.access
    if (accessToken === undefined) {
      setAndStoreJwt(undefined);
      return response;
    }
    setAndStoreJwt({'access': accessToken, 'refresh': refreshToken})
  }
  catch {
    setAndStoreJwt(undefined);
    return response;
  }

  if (data === undefined) {
    response = await fetchApiSingle(endpoint, accessToken);
  }
  else {
    response = await fetchApiSingle(endpoint, data, accessToken);
  }

  return response;
}
