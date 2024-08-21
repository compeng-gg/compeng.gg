interface ButtonProps {
  kind: 'primary' | 'secondary';
  onClick?: (event: React.MouseEvent<HTMLButtonElement, MouseEvent>) => void;
  type?: 'button' | 'submit' | 'reset';
  children: React.ReactNode;
}

function Button({ kind, onClick, type, children }: ButtonProps) {
  const baseClasses = 'px-4 py-2 rounded text-sm text-white cursor-pointer transition-transform transform active:scale-95 bg-blue-500 hover:bg-blue-600';
  const kindClasses =  kind === 'primary'
    ? 'bg-blue-500'
    : 'bg-gray-700';

  return (
    <button
      className={`${baseClasses} ${kindClasses}`}
      {...(type && { type })}
      {...(onClick && { onClick })}
    >
      {children}
    </button>
  );
}

export default Button;
