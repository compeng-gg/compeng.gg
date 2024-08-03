import LoginRequired from '@/app/lib/login-required';

import Main from '@/app/ui/main';
import Navbar from '@/app/ui/navbar';

function Course({ params }: { params: { slug: string } }) {
  return (
    <>
      <Navbar />
      <Main>
        <p>Listing for course: {params.slug}</p>
      </Main>
    </>
  );
}

export default function Page({ params }: { params: { slug: string } }) {
  return (
    <LoginRequired>
      <Course params={params} />
    </LoginRequired>
  );
}
