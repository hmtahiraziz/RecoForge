import React from 'react';

import { Form } from './components/Form';

export default function SignIn() {
  return (
    <main className="pt-16 flex items-center justify-center">
      <div className="max-w-[384px] w-full flex flex-col gap-6 p-8">
        <h1 className="text-heading-h2 text-textcolor-primary text-left w-full">Login</h1>

        <Form />
      </div>
    </main>
  );
}
