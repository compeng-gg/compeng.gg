import LoginRequired from '@/app/lib/login-required';
import Main from '@/app/ui/main';
import Navbar from '@/app/ui/navbar';
import H2 from '@/app/ui/h2';


function Labs({ params }: { params: { slug: string, lab_slug: string } }) {
    return (
    <>
      <Navbar />
      <Main>
            <H2>Grade for {params.lab_slug}:</H2>
      </Main>
    </>
    );
}


export default function Page({ params }: { params: { slug: string, lab_slug: string } }) {
    return (
      <LoginRequired>
        <Labs params={params} />
      </LoginRequired>
    );
  }