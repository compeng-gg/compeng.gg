'use client';

import { useParams } from 'next/navigation';

import LoginRequired from '@/app/lib/login-required';
import Main from '@/app/ui/main';
import Navbar from '@/app/ui/navbar';
import H2 from '@/app/ui/h2';

function Labs() {
  const params = useParams<{ course_slug: string, lab_slug: string }>();

  return (
  <>
    <Navbar />
    <Main>
          <H2>Grade for {params.course_slug} {params.lab_slug}:</H2>
    </Main>
  </>
  );
}


export default function Page() {
    return (
      <LoginRequired>
        <Labs />
      </LoginRequired>
    );
  }