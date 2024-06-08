"use client";

function getCookie(name: string) {
    let cookieValue = "";
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

export function fetchApi(input: string, data: any) {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v0';
  var csrftoken = getCookie('csrftoken');
  return fetch(apiUrl + input,
        {
            mode: "cors",
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": process.env.NEXT_PUBLIC_ORIGIN || "http://localhost:3000",
                "X-CSRFToken": csrftoken,
            },
            credentials: "include",
            body: JSON.stringify(data),
        }
  )
}
