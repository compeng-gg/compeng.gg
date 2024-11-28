import { fetchApi } from "@/app/lib/api";
/**
 * Fetches the username of the current user.
 * @param {string} jwt - The JWT token for authentication.
 * @param {Function} setAndStoreJwt - Function to update and store the JWT.
 * @returns {Promise<string>} - The username of the authenticated user.
 */
export async function fetchUserName(jwt: string, setAndStoreJwt: Function): Promise<string> {
    try {
        const res = await fetchApi(jwt, setAndStoreJwt, "users/self/", "GET");
        const data = await res.json();
        return data.username; // Return the username from the API response
    } catch (error) {
        console.error("Failed to fetch username", error);
        throw new Error("Failed to fetch username");
    }
}