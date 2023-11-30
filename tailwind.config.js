/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["templates/**/*.{html,js}"],
  theme: {
    extend: {
        colors:{
            'primary': {
                light: '#89CFF3',
                DEFAULT: '#00A9FF',
            },
            'secondary': {
                light: '#606470',
                DEFAULT: '#323643',
            },
        }
    },
    container: {
        center: true,
        padding: '20px',
    },
  },

  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    function ({ addComponents }) {
        addComponents({
            '.container': {
                maxWidth: '100%',
                '@screen sm': {
                    maxWidth: '100%',
                },
                '@screen md': {
                    maxWidth: '100%',
                },
                '@screen lg': {
                    maxWidth: '100%',
                },
                '@screen xl': {
                    maxWidth: '1152px',
                },
            }
        })
    },
  ]
}

