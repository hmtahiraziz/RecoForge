
import { FormContainer } from './components/FormContainer';

export default function Onboarding() {
  return (
    <main className="pt-[176px] flex flex-col items-center bg-pw-surfacecolor-primary min-h-screen p-6">
      <div className="max-w-[684px] w-full gap-10 flex flex-col">
        <FormContainer />
      </div>
    </main>
  );
}
