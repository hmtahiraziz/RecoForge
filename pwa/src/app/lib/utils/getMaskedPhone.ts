export const getMaskedPhone = (value: string) => {
  const cleanedValue = value.replace(/\D/g, '');

  if (cleanedValue.length <= 2) {
    return cleanedValue;
  } else if (cleanedValue.length <= 6) {
    return `${cleanedValue.slice(0, 2)} ${cleanedValue.slice(2)}`;
  } else {
    return `${cleanedValue.slice(0, 2)} ${cleanedValue.slice(2, 6)} ${cleanedValue.slice(6, 10)}`;
  }
};
