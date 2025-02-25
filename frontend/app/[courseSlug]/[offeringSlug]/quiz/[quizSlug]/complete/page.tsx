import Navbar from "@/app/components/navbar";
import LoginRequired from "@/app/lib/login-required";



export default function Page({ params} : {params: {courseSlug: string, offeringSlug: string, quizSlug: string}}) {
    const { courseSlug, offeringSlug, quizSlug } = params;

    return (
        <LoginRequired>
            <Navbar />
            <div style={{marginTop: "10%", display: "flex", flexDirection: "column", gap: "10px", alignItems: "center"}}>
                <h1>{`Your submission for ${quizSlug} has been recorded`}</h1>
                <h1>Thank you!</h1>
            </div>
        </LoginRequired>
    )
}
