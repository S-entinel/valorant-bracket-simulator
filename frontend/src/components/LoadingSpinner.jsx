function LoadingSpinner({ size = 'md', message = '' }) {
    const sizes = {
      sm: 'w-4 h-4',
      md: 'w-8 h-8',
      lg: 'w-12 h-12',
      xl: 'w-16 h-16'
    };
  
    return (
      <div className="flex flex-col items-center justify-center gap-3">
        <div className="relative">
          <div className={`${sizes[size]} border-4 border-gray-700 border-t-valorant-red rounded-full animate-spin`}></div>
        </div>
        {message && (
          <p className="text-gray-400 text-sm animate-pulse">{message}</p>
        )}
      </div>
    );
  }
  
  export default LoadingSpinner;