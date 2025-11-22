import { Dimensions } from 'react-native';

const { width, height } = Dimensions.get('window');

// Define a modern, eco-friendly color palette
const colors = {
    primary: '#2A9D8F', // Teal green - main action color
    secondary: '#E9C46A', // Yellow - accents, highlights
    background: '#F8F9FA', // Light gray - main background
    surface: '#FFFFFF', // White - card backgrounds, inputs
    text: '#264653', // Dark blue/green - primary text
    textSecondary: '#6C757D', // Gray - secondary text, placeholders
    error: '#E76F51', // Orange/Red - error messages
    success: '#2A9D8F', // Using primary for success indication
    border: '#DEE2E6', // Light gray - borders
    disabled: '#CED4DA', // Lighter gray - disabled elements
};

// Define typography styles
const typography = {
    h1: {
        fontSize: 28,
        fontWeight: 'bold',
        color: colors.text,
        marginBottom: 16,
    },
    h2: {
        fontSize: 24,
        fontWeight: 'bold',
        color: colors.text,
        marginBottom: 12,
    },
    h3: {
        fontSize: 20,
        fontWeight: '600',
        color: colors.text,
        marginBottom: 8,
    },
    body1: {
        fontSize: 16,
        color: colors.text,
        lineHeight: 24,
    },
    body2: {
        fontSize: 14,
        color: colors.textSecondary,
        lineHeight: 20,
    },
    button: {
        fontSize: 16,
        fontWeight: 'bold',
        color: colors.surface, // White text on buttons
    },
    caption: {
        fontSize: 12,
        color: colors.textSecondary,
    },
};

// Define spacing units
const spacing = {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
};

// Define common layout styles
const layout = {
    container: {
        flex: 1,
        backgroundColor: colors.background,
        padding: spacing.md,
    },
    centered: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: colors.background,
        padding: spacing.md,
    },
    row: {
        flexDirection: 'row',
        alignItems: 'center',
    },
    shadow: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
    },
};

// Define component-specific styles (can be expanded)
const components = {
    input: {
        height: 50,
        backgroundColor: colors.surface,
        borderColor: colors.border,
        borderWidth: 1,
        borderRadius: 8,
        paddingHorizontal: spacing.md,
        fontSize: typography.body1.fontSize,
        color: colors.text,
        marginBottom: spacing.md,
    },
    button: {
        backgroundColor: colors.primary,
        paddingVertical: 14,
        paddingHorizontal: spacing.lg,
        borderRadius: 8,
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: 50,
        marginBottom: spacing.md,
    },
    buttonText: {
        ...typography.button,
    },
    buttonSecondary: {
        backgroundColor: 'transparent',
        borderColor: colors.primary,
        borderWidth: 1,
    },
    buttonSecondaryText: {
        ...typography.button,
        color: colors.primary,
    },
    card: {
        backgroundColor: colors.surface,
        borderRadius: 12,
        padding: spacing.md,
        marginBottom: spacing.md,
        ...layout.shadow,
    },
};

const theme = {
    colors,
    typography,
    spacing,
    layout,
    components,
    width,
    height,
};

export default theme;
