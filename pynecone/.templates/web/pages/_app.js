import { ChakraProvider, extendTheme } from "@chakra-ui/react";
import theme from "/utils/theme";

function MyApp({ Component, pageProps }) {
  return (
    <ChakraProvider theme={extendTheme(theme)}>
      <Component {...pageProps} />
    </ChakraProvider>
  );
}

export default MyApp;
