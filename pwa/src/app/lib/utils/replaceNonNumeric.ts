export function replaceNonNumeric(str: string) {
  const priceRegex = /[^0-9]/g;
  return str.replace(priceRegex, '');
}
