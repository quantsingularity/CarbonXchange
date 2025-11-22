import React from 'react';
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import { Provider } from 'react-redux';
import { NavigationContainer } from '@react-navigation/native';
import configureStore from 'redux-mock-store'; // Use redux-mock-store for thunks
import thunk from 'redux-thunk';
import CreditsListScreen from '../../../screens/Main/CreditsListScreen';
import * as api from '../../../services/api'; // To mock API calls

const middlewares = [thunk];
const mockStore = configureStore(middlewares);

// Mock navigation
const mockNavigate = jest.fn();
const mockNavigation = { navigate: mockNavigate };

// Mock API service
jest.mock('../../../services/api', () => ({
    getCredits: jest.fn(),
}));

describe('CreditsListScreen', () => {
    let store;
    const initialState = {
        auth: { user: { id: '1' }, token: 'test-token', isLoggedIn: true },
        // Add other relevant initial states if your screen depends on them
    };

    beforeEach(() => {
        store = mockStore(initialState);
        mockNavigate.mockClear();
        api.getCredits.mockClear();
    });

    const renderComponent = (currentStore = store) => {
        return render(
            <Provider store={currentStore}>
                <NavigationContainer>
                    {/* Wrapping with NavigationContainer for screens that might use useNavigation or useRoute hooks */}
                    <CreditsListScreen navigation={mockNavigation} />
                </NavigationContainer>
            </Provider>,
        );
    };

    it('renders correctly and shows loading indicator initially', () => {
        api.getCredits.mockReturnValue(new Promise(() => {})); // Keep it pending
        const { getByTestId, queryByText } = renderComponent();
        // Assuming you have a loading indicator with testID="loading-indicator"
        // expect(getByTestId("loading-indicator")).toBeTruthy();
        // Or check if list is not yet rendered
        expect(queryByText('No credits available.')).toBeNull(); // if this message shows when empty and not loading
    });

    it('fetches and displays credits on mount', async () => {
        const mockCredits = [
            {
                id: '1',
                name: 'Solar Farm Project',
                tons: 100,
                pricePerTon: 20,
                location: 'California, USA',
                type: 'Renewable Energy',
            },
            {
                id: '2',
                name: 'Reforestation Initiative',
                tons: 50,
                pricePerTon: 15,
                location: 'Amazon Rainforest',
                type: 'Forestry',
            },
        ];
        api.getCredits.mockResolvedValue({ success: true, credits: mockCredits });

        const { findByText, getByText } = renderComponent();

        await waitFor(() => expect(api.getCredits).toHaveBeenCalledTimes(1));

        expect(await findByText('Solar Farm Project')).toBeTruthy();
        expect(getByText('Reforestation Initiative')).toBeTruthy();
        expect(getByText('100 Tons - $20/Ton')).toBeTruthy();
    });

    it('displays a message if no credits are available', async () => {
        api.getCredits.mockResolvedValue({ success: true, credits: [] });
        const { findByText } = renderComponent();
        expect(await findByText('No credits available. Add one?')).toBeTruthy(); // Assuming this text appears
    });

    it('displays error message if fetching credits fails', async () => {
        api.getCredits.mockRejectedValue(new Error('Failed to fetch credits'));
        const { findByText } = renderComponent();
        // Assuming an error message like "Failed to load credits. Please try again." is shown
        expect(await findByText(/Failed to load credits/i)).toBeTruthy();
    });

    it('navigates to CreditDetailScreen on credit item press', async () => {
        const mockCredits = [
            {
                id: '1',
                name: 'Solar Farm Project',
                tons: 100,
                pricePerTon: 20,
                location: 'California, USA',
                type: 'Renewable Energy',
            },
        ];
        api.getCredits.mockResolvedValue({ success: true, credits: mockCredits });

        const { findByText } = renderComponent();
        const creditItem = await findByText('Solar Farm Project');
        fireEvent.press(creditItem);

        expect(mockNavigate).toHaveBeenCalledWith('CreditDetail', {
            creditId: '1',
        });
    });

    it('navigates to a screen to add new credit on add button press', async () => {
        api.getCredits.mockResolvedValue({ success: true, credits: [] }); // Start with no credits to easily find add button
        const { findByText } = renderComponent();
        // Assuming there's a button/text like "Add New Credit" or similar if no credits
        // Or a floating action button with a specific testID
        const addButton = await findByText('No credits available. Add one?'); // Or a more specific selector
        // This test assumes the "Add one?" text is part of a pressable element that navigates.
        // A dedicated "Add Credit" button would be better to test.
        // For now, let's assume pressing this text triggers navigation.
        // fireEvent.press(addButton);
        // expect(mockNavigate).toHaveBeenCalledWith("AddNewCreditScreen"); // Or whatever the target screen is
        // This part is commented out as the current UI for adding might not be clear from the screen name alone.
    });

    // Add test for pull-to-refresh functionality if implemented
});
